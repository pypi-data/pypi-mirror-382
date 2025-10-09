from typing import Optional

import numpy as np

try:
    import cv2
    import imageio
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_audioclips
except ImportError as e:
    raise ImportError(
        "Videos dependencies are not installed. Please install them using using pip install kiwi-booster[video]."
    ) from e


class ImageIOWrapper:
    """Wrapper class for imageio writer to mimic opencv VideoWriter"""

    def __init__(self, writer: imageio.core.request.Request):
        """Initializes the object.
        Args:
            writer (imageio.core.request.Request): Imageio writer object.
        """
        self.writer = writer

    def write(self, image: np.ndarray) -> None:
        """Writes image to the video file.
        Args:
            image (np.ndarray): Image to write to the video file.
                It should be RGB.
        """
        self.writer.append_data(image)

    def release(self) -> None:
        """Releases the video to close the file."""
        # To mimc what the context manager does to close the file
        # See imageio source file
        self.writer._request.finish()


class VideoWriter:
    """Class for writing video frames to a local file"""

    def __init__(
        self,
        video_path: str,
        fps: int,
        backend: str = "opencv",
        codec: str = "MP4V",
        imageio_kwargs: dict = {},
    ):
        """Initializes the object.

        Args:
            video_path (str): Local path to the video file.
            fps (int): FPS of the video.
            backend (str, optional): Backend to use for writing the video.
                Can be "opencv" or "imageio". Defaults to "opencv".
            codec (str, optional): Codec used to encode the video.
                Defaults to "MP4V".
            imageio_kwargs (dict, optional): Additional keyword arguments to pass
                to the imageio writer. Defaults to {}.
        """
        self.video_path = video_path
        self.fps = fps
        self.codec = codec
        self.backend = backend
        self.imageio_kwargs = imageio_kwargs
        self.writer = None
        self.frame_id = 0

        supported_backends = ["opencv", "imageio"]
        if self.backend not in supported_backends:
            raise ValueError(
                f"Backend {self.backend} is not supported. Use one of {supported_backends}"
            )

    def get_current_frame_id(self) -> int:
        """Returns the current frame id.

        Returns:
            int: Current frame id.
        """
        return self.frame_id

    def write_frame(self, frame: np.ndarray) -> None:
        """Writes frame to the video file.

        Args:
            frame (np.ndarray): Frame to write to the video file.
                It should be RGB.

        """
        if self.writer is None:
            if self.backend == "imageio":
                self.writer = ImageIOWrapper(
                    imageio.get_writer(
                        self.video_path, fps=self.fps, **self.imageio_kwargs
                    )
                )
            elif self.backend == "opencv":
                self.writer = cv2.VideoWriter(
                    self.video_path,
                    cv2.VideoWriter_fourcc(*self.codec),
                    int(self.fps),
                    frame.shape[:2][::-1],
                )

        self.writer.write(frame)
        self.frame_id += 1

    def release(self) -> None:
        """Releases the video to close the file."""
        if self.writer is not None:
            self.writer.release()

    def add_music(self, audio_path: str, output_path: Optional[str] = None) -> None:
        """Adds audio to the video.

        Args:
            audio_path (str): Local path to the audio file.
            output_path (str, optional): Local path to the output video file.
                If None, the output video will be saved with a '_music' suffix added
                to the video path. Defaults to None.
        """
        if output_path is None:
            # Add a suffix to the video path
            extension = self.video_path.split(".")[-1]
            output_path = self.video_path.replace(
                f".{extension}", f"_music.{extension}"
            )

        # Load the video and audio
        video_clip = VideoFileClip(self.video_path)
        audio_clip = AudioFileClip(audio_path)

        # Calculate the necessary number of audio loops
        video_duration = video_clip.duration
        audio_duration = audio_clip.duration
        loop_count = int(video_duration // audio_duration) + 1

        # Loop or trim the audio to match video duration
        audio_clips = [audio_clip] * loop_count
        looped_audio = concatenate_audioclips(audio_clips).subclip(0, video_duration)

        # Set the looped or trimmed audio to the video
        final_clip = video_clip.set_audio(looped_audio)

        # Write the output video file
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
