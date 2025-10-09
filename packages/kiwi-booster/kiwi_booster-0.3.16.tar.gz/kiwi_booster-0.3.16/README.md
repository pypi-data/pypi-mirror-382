<div id="top"></div>

<!-- PROJECT LOGO -->

<br />
<div align="center">
  <a href="https://github.com/kiwicampus/kiwi-booster">
    <img src="https://user-images.githubusercontent.com/26184787/227988899-7192c613-c651-4f45-ae9a-8dea254ccaca.png" alt="Logo" width="200" height="200">
  </a>
<h3 align="center"><font size="8">Kiwi Booster</font></h3>

<p align="center">
    Python utils and classes for KiwiBot AI&Robotics team<br>
    <a href="https://github.com/kiwicampus/kiwi-booster/pulls">Make a Pull Request</a>
    ·
    <a href="https://github.com/kiwicampus/kiwi-booster/issues">Report Bug</a>
    ·
    <a href="https://github.com/kiwicampus/kiwi-booster/issues">Request Feature</a>
</p>

</div>

---

<!-- TABLE OF CONTENTS -->

### Table of contents

- [About The Project](#about-the-project)
  - [MCAP ROSBag Decoder](#mcap-rosbag-decoder)
- [Getting started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
- [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

---

<!-- ABOUT THE PROJECT -->

## About The Project

This library contains utility functions and classes from Python that are commonly used in the AI&Robotics team. It is divided into 5 main sections:

- **common_utils**: Some common utils that are normally used in most of the projects.
  
  - kiwi_booster.loggers
    This module contains GCP and local loggers with a predefined format.
  
  - kiwi_booster.mixed
    This module contains miscellaneous utils from multiple objectives.
  
  - kiwi_booster.requests
    This module contains utils for working with HTTP requests.
  
  - kiwi_booster.video
    This module contains utils for working with videos. This includes the `VideoWriter` class, which is used to write videos in a predefined format. IMPORTANT: This class needs CV2 to be installed in the environment.

- **gcp_utils**: Utils that are related to the Google Cloud Platform.
  
  - kiwi_booster.gcp_utils.bigquery
    This module contains utils for working with BigQuery.
  
  - kiwi_booster.gcp_utils.kfp
    This module contains utils for working with Vertex (Kubeflow) Pipelines.
  
  - kiwi_booster.gcp_utils.secrets
    This module contains utils for working with Google Cloud Secrets Manager.
  
  - kiwi_booster.gcp_utils.storage
    This module contains utils for working with Google Cloud Storage.

- **ml_utils**: Utils that are related to Machine Learning.
  
  - kiwi_booster.ml_utils.benchmarks
    This module contains utils for benchmarking machine learning models.
  
  - kiwi_booster.ml_utils.prediction
    This module contains utils to handle the prediction of the semantic segmentation model.

- **decorators**: Decorators that are used to improve the codebase.

- **slack_utils**: Utils that are related to Slack.
  
- **mcap_utils**: Utils related to read and decode ROSbags messages in mcap format without the need of a ROS environment. More information on the next section.

### MCAP ROSBag Decoder

The mcap utils are designed as tools to decode MCAP ROSBags without needing a ROS environment. It supports various message types and provides a custom decoder factory for handling ROS2IDL-encoded messages.

**IDLDecoderFactory Class**
The IDLDecoderFactory class extends the DecoderFactory class. It is specifically designed to work with ROS2IDL encoded messages. The class provides a method decoder_for that returns a decoder for a given message encoding and schema. Currently, it uses a dummy decoder that does nothing but can be extended to use more complex decoders.

**Supported Messages**
The module supports decoding of the following message types:

- CompressedImage
- Image
- NavSatFix
- TFMessage
- Odometry
- PointCloud2

Each message type has a corresponding decode function that takes in the message and returns the decoded data along with some metadata.

**CompressedImage and Image**
The decode_compressed_image and decode_image functions decode `sensor_msgs/msg/CompressedImage` and `sensor_msgs/msg/Image` messages respectively. They return a tuple containing the image as a Numpy array and a metadata dictionary. The metadata includes the image format, the image's timestamp as a datetime object, the image's frame id, and the image's step (only for decode_image).

**NavSatFix**
The decode_navsatfix function decodes sensor_msgs/msg/NavSatFix messages. It returns a dictionary of the message's fields, the measurement's accuracy, and some metadata. The metadata includes the message's timestamp as a datetime object, the message's frame ID, the measurement's accuracy, the altitude, latitude, longitude, position covariance, and position covariance type of the measurement.

**TFMessage**
The decode_tfmessage function decodes tf2_msgs/msg/TFMessage messages. It returns a list of dictionaries of the transforms. Each dictionary includes the child frame id, frame id, timestamp as a datetime object, translation as a 3D vector, and rotation as a Quaternion.

**Odometry**
The decode_odometry function decodes nav_msgs/msg/Odometry messages. It returns a dictionary with the timestamp as a datetime object, frame id, child frame id, pose (including covariance, position as a 3D vector, and orientation as a Quaternion), twist (including covariance, linear as a 3D vector, and angular as a 3D vector), and covariance of the message.

**PointCloud2**
The decode_pointcloud function decodes sensor_msgs/msg/PointCloud2 messages. It returns a tuple containing the point cloud data as a Numpy array and a metadata dictionary. The metadata includes the message's timestamp as a datetime object, the message's frame ID, the point cloud's height, width, if the point cloud is dense, the point cloud's is_bigendian, the point cloud's point step, and the point cloud's row step.

**Reading Messages**
To read a message, call the corresponding decode function with the message as the argument. For example, to decode a CompressedImage message, you would do:

```python
image, metadata = decode_compressed_image(msg)
```

Where msg is the CompressedImage message to decode, the function returns the image as a Numpy array and the metadata as a dictionary.

Here is an example of how to use read and mcap file:

```python
from kiwi_booster.mcap_utils.decode import (
        IDLDecoderFactory,
        decode_compressed_image,
        decode_image,
        decode_navsatfix,
        decode_odometry,
        decode_image_marker,
        decode_pointcloud
    )
from mcap.reader import make_reader
from mcap_ros2.decoder import DecoderFactory

# Initialize the list for all the topics
topics = {topic: [] for topic in topics_to_read}

# Read the rosbag file
with open(rosbag_path, "rb") as f:
    reader = make_reader(
        f, decoder_factories=[DecoderFactory(), IDLDecoderFactory()]
    )
    for schema, channel, _, decoded_msg in reader.iter_decoded_messages(
        log_time_order=True # This is used to return the messages in the real time order 
    ):
        if channel.topic in topics_to_read:
            if schema.name == "sensor_msgs/msg/CompressedImage":
                image, image_metadata = decode_compressed_image(decoded_msg)
                topics[channel.topic].append([image, image_metadata])
            elif schema.name == "sensor_msgs/msg/NavSatFix":
                latlon = decode_navsatfix(decoded_msg)
                topics[channel.topic].append(latlon)
            elif schema.name == "nav_msgs/msg/Odometry":
                odometry = decode_odometry(decoded_msg)
                topics[channel.topic].append(odometry)
            elif schema.name == "sensor_msgs/msg/Image":
                image, image_metadata = decode_image(decoded_msg)
                topics[channel.topic].append([image, image_metadata])
            elif schema.name == "visualization_msgs/msg/ImageMarker":
                marker_array = decode_image_marker(decoded_msg)
                topics[channel.topic].append(marker_array)
            elif schema.name == "sensor_msgs/msg/PointCloud2":
                cloud, metadata = decode_pointcloud(decoded_msg)
                topics[channel.topic].append([cloud, metadata])
            else:
                raise ValueError(f"Unknown schema {schema.name}")
```

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- GETTING STARTED -->

## Getting started

### Installation

To install the package, simply run the following command:

```sh
pip install kiwi-booster
```

### Usage

To use the package, we recommend using relative imports for each function or class you want to import to improve readability. For example, if you want to use the `SlackBot` class, you can import it as follows:

```python
from kiwi_booster.slack_utils import SlackBot

slack_bot = SlackBot(
        SLACK_TOKEN,
        SLACK_CHANNEL_ID,
        SLACK_BOT_IMAGE_URL,
        image_alt_text="Bot description",
)
```

Or any decorator as follows:

```python
from kiwi_booster.decorators import try_catch_log

@try_catch_log
def my_function():
    # Do something
```

As well, we recommend importing them in a separate section from the rest of the imports.

<p align="right">(<a href="#top">back to top</a>)</p>

---

<!-- CONTRIBUTING -->


## Publishing to pypi

Authenticate first with pypi. Generate a token in pypi account settings and run the following command:

```sh
poetry config pypi-token.pypi <your-token>
```

Then, run the following commands:

```sh

poetry build
poetry publish
```


## Contributing

If you'd like to contribute to Kiwi Booster, please feel free to submit a pull request! We're always looking for ways to improve our codebase and make it more useful to a wider range of use cases. You can also request a new feature by submitting an issue.

### License

Kiwi Booster is licensed under the GNU license. See the LICENSE file for more information.

### Contact

Sebastian Hernández Reyes - Machine Learning Engineer - [Mail contact](mailto:juan.hernandez@kiwibot.com)

Carlos Alvarez - Machine Learning Engineer Lead - [Mail contact](mailto:carlos.alvarez@kiwibot.com)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Template developed by the ML Team :D-->
