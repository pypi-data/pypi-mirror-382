import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from django_sync_env import settings


class SyncEnvNotifications:
    enabled = False
    client = None

    def __init__(self):
        if settings.SYNC_ENV_NOTIFICATION_CONFIG:
            self.enabled = True
            slack_token = settings.SYNC_ENV_NOTIFICATION_CONFIG.get("SLACK_API_TOKEN", None)
            self.client = WebClient(token=slack_token)

    def send_slack_message(self, blocks=None, text=None):
        if settings.ENVIRONMENT in settings.SYNC_ENV_NOTIFICATION_CONFIG.get("ENVS_TO_SEND_SLACK_MSGS"):
            try:
                response = self.client.chat_postMessage(
                    channel=settings.SYNC_ENV_NOTIFICATION_CONFIG.get("SLACK_CHANNEL_ID"),
                    blocks=blocks,
                    text=text
                )
                logging.info(response)
                return response
            except SlackApiError as e:
                # You will get a SlackApiError if "ok" is False
                logging.error(e.response["error"])  # str like 'invalid_auth', 'channel_not_found'
                return None
