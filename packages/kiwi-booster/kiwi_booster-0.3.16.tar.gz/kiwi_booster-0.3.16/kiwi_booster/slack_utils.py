"""
Module containing the SlackBot class.
"""

from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackBot:
    """Class to interface with slack as a Bot"""

    def __init__(
        self,
        slack_token: str,
        slack_channel_id: str,
        bot_image_url: Optional[str] = None,
        report_header: str = "Bot report",
        image_alt_text: str = "Welcome to the Bot report",
    ):
        """
        Object class constructor for the Slack Bot class.

        Arguments:
            slack_token(str): Secret token for accessing to the Slack API.
            slack_channel_id(str): ID of the channel where the message will be published.
            bot_image_url(str): URL Of the image to be displayed within the message
                sent to the Slack channel.
            report_header(str): Header of the message to be sent to the Slack channel.
            image_alt_text(str): Alt text for the image to be displayed within the message
                sent to the Slack channel.
        """

        self.token = slack_token
        self.channel_id = slack_channel_id
        self.client = WebClient(token=self.token)
        self.color_map = {
            "error": "#f2000c",
            "warn": "#f2de00",
            "info": "#2eb886",
        }
        self.report_header = report_header
        self.bot_image = bot_image_url
        self.image_alt_text = image_alt_text

    def create_attachment(self, type: str = "info", **kwargs) -> list:
        """
        Sends the fields included in the Kwargs through the slack SDK
            into the company's Workspace within the 'anonymization_report'
            channel.

        Args:
            type(str): Message level withing the 'info', 'warn' and 'error'
                categories.
            **kwargs: Key-value pairs of the message to be sent to the Slack

        Returns:
            block(list): List containing the the block structure for composing
                the Slack message.
        """

        block = []
        color = (
            self.color_map[type]
            if type in self.color_map.keys()
            else self.color_map["info"]
        )
        for type, message in kwargs.items():
            block.append(
                {
                    "color": f"{color}",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{type}*:  \n {message}",
                            },
                        }
                    ],
                    "fallback": self.report_header,
                }
            )

        # Adds the image only into the first block message
        if self.bot_image is not None:
            block[0]["blocks"][0]["accessory"] = {
                "type": "image",
                "image_url": self.bot_image,
                "alt_text": self.image_alt_text,
            }
        return block

    def send_message(self, **kwargs) -> None:
        """
        Sends the fields included in the Kwargs through the slack SDK into the
        company's Workspace.

        Args:
            **kwargs: Key-value pairs of the message to be sent to the Slack
                type(str): Message level withing the 'info', 'warn' and 'error'
                    categories.

        """
        attachments = self.create_attachment(**kwargs)
        try:
            self.client.chat_postMessage(
                channel=self.channel_id,
                attachments=attachments,
                text=self.report_header,
            )
        except SlackApiError as e:
            print(f"Error when writing to the slack API: {e}")


if __name__ == "__main__":
    import os

    token = os.getenv("SLACK_OAUTH_TOKEN")
    channel_id = os.getenv("SLACK_BOT_IMAGE_URL")
    bot = SlackBot(token, channel_id)
    bot.send_message(
        content="AI Report bot test",
        message="This is a test",
        type="info",
    )
