import math
import struct
import sys
from enum import Enum
from typing import Generator, List, Optional, Tuple, Union


class PointField(Enum):
    "Class to mimic ROS PointField from sensor_msgs.msg package"
    INT8 = 1
    UINT8 = 2
    INT16 = 3
    UINT16 = 4
    INT32 = 5
    UINT32 = 6
    FLOAT32 = 7
    FLOAT64 = 8


_DATATYPES = {}
_DATATYPES[PointField.INT8.value] = ("b", 1)
_DATATYPES[PointField.UINT8.value] = ("B", 1)
_DATATYPES[PointField.INT16.value] = ("h", 2)
_DATATYPES[PointField.UINT16.value] = ("H", 2)
_DATATYPES[PointField.INT32.value] = ("i", 4)
_DATATYPES[PointField.UINT32.value] = ("I", 4)
_DATATYPES[PointField.FLOAT32.value] = ("f", 4)
_DATATYPES[PointField.FLOAT64.value] = ("d", 8)


def read_points(
    cloud: "sensor_msgs.msg.PointCloud2",  # noqa: F821
    field_names: Optional[List[str]] = None,
    skip_nans: bool = False,
    uvs: List[Tuple[int, int]] = [],
) -> Generator[List[Union[int, float]], None, None]:
    """
    Read points from a PointCloud2 message.

    Args:
        cloud (sensor_msgs.msg.PointCloud2): The point cloud to read from.
        field_names (Optional[List[str]]): The names of fields to read. If None, all fields are read. Defaults to None.
        skip_nans (bool): If True, points with NaN values are not returned. Defaults to False.
        uvs (List[Tuple[int, int]]): Coordinates of specific points to return. Defaults to an empty list.

    Returns:
        Generator: Yields a list of values for each point.
    """

    fmt = _get_struct_fmt(cloud.is_bigendian, cloud.fields, field_names)
    width, height, point_step, row_step, data, isnan = (
        cloud.width,
        cloud.height,
        cloud.point_step,
        cloud.row_step,
        cloud.data,
        math.isnan,
    )
    unpack_from = struct.Struct(fmt).unpack_from

    if skip_nans:
        if uvs:
            for u, v in uvs:
                p = unpack_from(data, (row_step * v) + (point_step * u))
                has_nan = False
                for pv in p:
                    if isnan(pv):
                        has_nan = True
                        break
                if not has_nan:
                    yield p
        else:
            for v in range(height):
                offset = row_step * v
                for u in range(width):
                    p = unpack_from(data, offset)
                    has_nan = False
                    for pv in p:
                        if isnan(pv):
                            has_nan = True
                            break
                    if not has_nan:
                        yield p
                    offset += point_step
    else:
        if uvs:
            for u, v in uvs:
                yield unpack_from(data, (row_step * v) + (point_step * u))
        else:

            for v in range(height):
                offset = row_step * v
                for u in range(width):
                    yield unpack_from(data, row_step * v + point_step * u)
                    offset += point_step


def _get_struct_fmt(
    is_bigendian: bool,
    fields: List["sensor_msgs.msg.PointField"],  # noqa: F821
    field_names: Optional[List[str]] = None,
) -> str:
    """
    Generates a struct format string for unpacking data from a PointCloud2 message based on the
    endianness, specified fields, and field names.

    Args:
        is_bigendian (bool): Indicates if the data is stored in big-endian byte order.
        fields (List[sensor_msgs.msg.PointField]): The fields from the PointCloud2 message that
            describe the data structure.
        field_names (Optional[List[str]]): Names of the fields to include in the format.
            If None, includes all fields. Defaults to None.

    Returns:
        str: A string representing the struct format to be used for unpacking the point cloud data.

    Raises:
        ValueError: If an unknown datatype is encountered in the fields.
    """

    fmt = ">" if is_bigendian else "<"

    offset = 0
    for field in (
        f
        for f in sorted(fields, key=lambda f: f.offset)
        if field_names is None or f.name in field_names
    ):
        if offset < field.offset:
            fmt += "x" * (field.offset - offset)
            offset = field.offset
        if field.datatype not in _DATATYPES:
            print(
                "Skipping unknown PointField datatype [%d]" % field.datatype,
                file=sys.stderr,
            )
        else:
            datatype_fmt, datatype_length = _DATATYPES[field.datatype]
            fmt += field.count * datatype_fmt
            offset += field.count * datatype_length

    return fmt
