import html
import logging

import requests
from loguru import logger

from src.core.settings import Settings


class TelegramLoggerSink(logging.Handler):
    def __init__(self, settings: Settings) -> None:
        self.token = settings.TELEGRAM_TOKEN
        self.chat_ids = settings.ADMINISTRATOR_IDS
        self.project_flag = settings.PROJECT_FLAG
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        self.api_url_photo = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        super().__init__()

    def send_message(self, message: str, image_path: str = None) -> None:
        """
        Sends a message to multiple chat IDs.
        Args:
            message (str): The message to be sent.
            
        Returns:
            None
        """
        try:
            project_flag = self.project_flag + "\n"

            for chat_id in self.chat_ids:
                payload = {
                    "chat_id": chat_id,
                    "text": html.escape(project_flag + message),
                    "parse_mode": "HTML",
                }
                requests.post(self.api_url, data=payload)

                if image_path:
                    self.send_photo(chat_id, image_path)

        except Exception:
            logger.warning("Error in send replies loop")
    
    def send_photo(self, chat_id: str, image_path: str) -> None:
        """
        Sends a photo to a specific chat ID.
        Args:
            chat_id (str): Unique identifier for the target chat.
            image_path (str): Photo to send. Pass a file_id as String to send a photo that exists on the Telegram servers (recommended), pass an HTTP URL as a String for Telegram to get a photo from the Internet, or upload a new photo using multipart/form-data. The photo must be at most 10 MB in size. The photo's width and height must not exceed 10000 in total. Width and height ratio must be at most 20.
        Returns:
            None
        """
        try:
            with open(image_path, 'rb') as image_file:
                files = {'photo': image_file}
                data = {
                    "chat_id": chat_id
                }
                requests.post(self.api_url_photo, files=files, data=data)
        except Exception as e:
            logger.warning(f"Error sending photo. Error: {e}")

    def emit(self, record: logging.LogRecord) -> None:
        photo = getattr(record, 'photo_path', None)
        text = self.format(record)
        self.send_message(message=text, image_path=photo)


def init_logger(settings: Settings) -> None:
    standard_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # handler config
    basic_handler = logging.StreamHandler()
    basic_handler.setLevel(logging.INFO)
    basic_handler.setFormatter(standard_formatter)

    # telegram handler
    telegram_handler = TelegramLoggerSink(settings)
    telegram_handler.setLevel(logging.ERROR)
    telegram_handler.setFormatter(standard_formatter)

    # logger config
    app_logger = logging.getLogger()
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(basic_handler)
    app_logger.addHandler(telegram_handler)
    app_logger.propagate = False