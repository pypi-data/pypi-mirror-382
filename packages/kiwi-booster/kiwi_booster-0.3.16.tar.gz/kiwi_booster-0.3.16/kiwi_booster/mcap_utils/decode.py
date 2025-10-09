"""
Utility functions for decoding messages from mcap rosbags
"""

# Imports
import io
from datetime import datetime, timedelta
from typing import Any, Callable, List, Optional, Tuple

import numpy as np
from mcap.records import Schema
from mcap.well_known import MessageEncoding, SchemaEncoding
from mcap_ros2.decoder import DecoderFactory
from PIL import Image as PILImage

from .pointcloud import read_points


class IDLDecoderFactory(DecoderFactory):
    """
    Custom Decoder Factory class that extends the DecoderFactory. It is designed to be
    used with ROS2IDL encoded messages, it provides a method to get a decoder for a given
    message encoding and schema. Right now just a dummy decoder is used.
    """

    def decoder_for(
        self, message_encoding: str, schema: Optional[Schema]
    ) -> Optional[Callable[[bytes], None]]:
        """
        Returns a decoder for the given message encoding and schema.
        Right now just a dummy decoder is used.

        Args:
            message_encoding (str): The message encoding.
            schema (Optional[Schema]): The schema of the ROS message.

        Returns:
            Optional[Callable[[bytes], None]]: The decoder function or None.
        """
        if (
            message_encoding != MessageEncoding.CDR
            or schema is None
            or schema.encoding != SchemaEncoding.ROS2IDL
        ):
            return None

        decoder = self._decoders.get(schema.id)

        def dummy_decoder(data: bytes) -> None:
            """
            A dummy decoder that does nothing.

            Args:
                data: The data to decode.

            Returns:
                Nothing
            """
            return None

        if decoder is None:
            decoder = dummy_decoder
            self._decoders[schema.id] = decoder
        return decoder


# Utility functions to decode specific messages from mcap rosbags


def stamp_to_datetime(stamp: Any) -> datetime:
    """
    Converts a ROS2 Time message to a datetime object.

    Args:
        stamp (Time): The Time message to convert.

    Returns:
        datetime: The timestamp as a datetime object.
    """
    return datetime.fromtimestamp(stamp.sec) + timedelta(
        microseconds=stamp.nanosec / 1000
    )


def decode_compressed_image(msg: Any) -> Tuple[np.ndarray, dict]:
    """
    Decodes a sensor_msgs/msg/CompressedImage message into a tupple of the image and some
    metadata.

    Args:
        msg (CompressedImage): The CompressedImage message to decode.

    Returns:
        Tuple(np.ndarray, dict): The image as a Numpy array and the following metadata:
            - format: The image incoming format.
            - timestamp: The timestamp of the image as a datetime object.
            - frame_id: The frame id of the image.
    """

    image = PILImage.open(io.BytesIO(msg.data))
    image = np.array(image)

    log_time = stamp_to_datetime(msg.header.stamp)

    metadata = {
        "format": msg.format,
        "timestamp": log_time,
        "frame_id": msg.header.frame_id,
    }
    return image, metadata


def decode_image(msg: Any) -> Tuple[np.ndarray, dict]:
    """
    Decodes a sensor_msgs/msg/Image message into a tuple of the image and some metadata.

    Args:
        msg (Image): The Image message to decode.

    Returns:
        Tuple[np.ndarray, dict]: The image as a Numpy array and the following metadata:
            - format: The image incoming format.
            - timestamp: The timestamp of the image as a datetime object.
            - frame_id: The frame id of the image.
            - step: The step of the image.
    """
    height = msg.height
    width = msg.width
    format = msg.encoding

    dtype = np.uint8
    if "mono" in format:
        channel = 1
    elif "rgb" in format or "bgr" in format:
        channel = 3
    elif "rgba" in format or "bgra" in format:
        channel = 4
    elif "16UC1" in format:  # for example depth maps
        channel = 1
        dtype = np.uint16
    else:
        raise ValueError(f"Unsupported image format: {format}")

    image = np.frombuffer(msg.data, dtype=dtype).reshape((height, width, channel))
    image = image.squeeze()  # Remove the channel dimension if it is 1

    log_time = stamp_to_datetime(msg.header.stamp)

    metadata = {
        "format": format,
        "timestamp": log_time,
        "frame_id": msg.header.frame_id,
        "step": msg.step,
    }
    return image, metadata


def decode_pointcloud(msg: Any) -> Tuple[np.ndarray, dict]:
    """
    Decodes a sensor_msgs/msg/PointCloud2 message into a tuple of the point cloud and some
    metadata.

    Args:
        msg (PointCloud2): The PointCloud2 message to decode.

    Returns:
        Tuple[np.ndarray, dict]: The point cloud as a Numpy array and the following metadata:
            - timestamp: The timestamp of the point cloud as a datetime object.
            - frame_id: The frame id of the point cloud.
            - is_dense: The is_dense flag of the point cloud.
            - point_step: The point step of the point cloud.
            - row_step: The row step of the point cloud.
            - is_bigendian: The is_bigendian flag of the point cloud.
            - height: The height of the point cloud.
            - width: The width of the point cloud.

    """
    data = np.array(list(read_points(msg)))
    metadata = {
        "timestamp": stamp_to_datetime(msg.header.stamp),
        "frame_id": msg.header.frame_id,
        "is_dense": msg.is_dense,
        "point_step": msg.point_step,
        "row_step": msg.row_step,
        "is_bigendian": msg.is_bigendian,
        "height": msg.height,
        "width": msg.width,
    }
    return data, metadata


def decode_navsatfix(msg: Any) -> dict:
    """
    Decodes a sensor_msgs/msg/NavSatFix message into a dictionary of the message's fields
    plus the accuracy of the measurement and some metadata.

    Args:
        msg (NavSatFix): The NavSatFix message to decode.

    Returns:
        dict: A dictionary of the message's fields plus the accuracy of the measurement and
        the following metadata:
            - timestamp: The timestamp of the message as a datetime object.
            - frame_id: The frame id of the message.
            - accuracy: The accuracy of the measurement.
            - altitude: The altitude of the measurement.
            - latitude: The latitude of the measurement.
            - longitude: The longitude of the measurement.
            - position_covariance: The position covariance of the measurement.
            - position_covariance_type: The position covariance type of the measurement.

    """
    log_time = stamp_to_datetime(msg.header.stamp)
    return {
        "timestamp": log_time,
        "frame_id": msg.header.frame_id,
        "altitude": msg.altitude,
        "latitude": msg.latitude,
        "longitude": msg.longitude,
        "position_covariance": msg.position_covariance,
        "position_covariance_type": msg.position_covariance_type,
        "accuracy": np.sqrt(msg.position_covariance[0]),
    }


def decode_tfmessage(msg: Any) -> List[dict]:
    """
    Decodes a tf2_msgs/msg/TFMessage message into a list of dictionaries of the
    transforms.

    Args:
        msg (TFMessage): The TFMessage message to decode.

    Returns:
        List[dict]: A list of dictionaries of the transforms with the following fields:
            - child_frame_id: The child frame id of the transform.
            - frame_id: The frame id of the transform.
            - timestamp: The timestamp of the transform as a datetime object.
            - translation: The translation of the transform, is a dictionary representing
            a 3D vector with the following fields:
                - x: The x coordinate of the translation.
                - y: The y coordinate of the translation.
                - z: The z coordinate of the translation.
            - rotation: The rotation of the transform, is a dictionary representing a
            Quaternion with the following fields:
    """
    decoded_transforms = []
    for transform in msg.transforms:
        decoded_transforms.append(
            {
                "child_frame_id": transform.child_frame_id,
                "frame_id": transform.header.frame_id,
                "timestamp": stamp_to_datetime(transform.header.stamp),
                "translation": {
                    "x": transform.transform.translation.x,
                    "y": transform.transform.translation.y,
                    "z": transform.transform.translation.z,
                },
                "rotation": {
                    "x": transform.transform.rotation.x,
                    "y": transform.transform.rotation.y,
                    "z": transform.transform.rotation.z,
                    "w": transform.transform.rotation.w,
                },
            }
        )
    return decoded_transforms


def decode_odometry(msg: Any) -> dict:
    """
    Decodes a nav_msgs/msg/Odometry message into a dictionary with the following fields:
        - timestamp: The timestamp of the message as a datetime object.
        - frame_id: The frame id of the message.
        - child_frame_id: The child frame id of the message.
        - pose: The pose of the message, is a dictionary representing a Pose with the
        following fields:
            - covariance: The covariance of the pose.
            - position: The position of the pose, is a dictionary representing a 3D vector
            with the following fields:
                - x: The x coordinate of the position.
                - y: The y coordinate of the position.
                - z: The z coordinate of the position.
            - orientation: The orientation of the pose, is a dictionary representing a
            Quaternion with the following fields:
                - x: The x coordinate of the orientation.
                - y: The y coordinate of the orientation.
                - z: The z coordinate of the orientation.
                - w: The w coordinate of the orientation.
        - twist: The twist of the message, is a dictionary representing a Twist with the
        following fields:
            - covariance: The covariance of the twist.
            - linear: The linear of the twist, is a dictionary representing a 3D vector
            with the following fields:
                - x: The x coordinate of the linear.
                - y: The y coordinate of the linear.
                - z: The z coordinate of the linear.
            - angular: The angular of the twist, is a dictionary representing a 3D vector
            with the following fields:
                - x: The x coordinate of the angular.
                - y: The y coordinate of the angular.
                - z: The z coordinate of the angular.
        - covariance: The covariance of the message.
    """
    return {
        "timestamp": stamp_to_datetime(msg.header.stamp),
        "frame_id": msg.header.frame_id,
        "child_frame_id": msg.child_frame_id,
        "pose": {
            "covariance": msg.pose.covariance,
            "position": {
                "x": msg.pose.pose.position.x,
                "y": msg.pose.pose.position.y,
                "z": msg.pose.pose.position.z,
            },
            "orientation": {
                "x": msg.pose.pose.orientation.x,
                "y": msg.pose.pose.orientation.y,
                "z": msg.pose.pose.orientation.z,
                "w": msg.pose.pose.orientation.w,
            },
        },
        "twist": {
            "covariance": msg.twist.covariance,
            "linear": {
                "x": msg.twist.twist.linear.x,
                "y": msg.twist.twist.linear.y,
                "z": msg.twist.twist.linear.z,
            },
            "angular": {
                "x": msg.twist.twist.angular.x,
                "y": msg.twist.twist.angular.y,
                "z": msg.twist.twist.angular.z,
            },
        },
        "covariance": msg.ros_msg.pose.covariance,
    }


def decode_image_marker(msg: Any) -> Tuple[dict, dict, dict]:
    """
    Decodes a visualization_msgs/msg/ImageMarker message into a tuple of the markers and
    some metadata.

    Args:
        msg (ImageMarker): The ImageMarker message to decode.

    Returns:
        Tuple[dict, dict, dict]: The position, points as dictionaries with the "x" and "y"
        points and the following metadata:
            - timestamp: The timestamp of the message as a datetime object.
            - frame_id: The frame id of the message.
            - type: The type of the message.
            - action: The action of the message.
    """

    position = {
        "x": msg.position.x,
        "y": msg.position.y,
        # "z": msg.position.z, # z is always 0
    }

    points = []
    for point in msg.points:
        points.append(
            {
                "x": point.x,
                "y": point.y,
                # "z": point.z, # z is always 0
            }
        )
    log_time = stamp_to_datetime(msg.header.stamp)

    metadata = {
        "timestamp": log_time,
        "frame_id": msg.header.frame_id,
        "type": msg.type,
        "action": msg.action,
    }
    return position, points, metadata
