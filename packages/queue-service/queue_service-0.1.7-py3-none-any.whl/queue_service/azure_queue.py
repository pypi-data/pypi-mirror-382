from azure.storage.queue import QueueClient as AzureQueueClientSDK
from .exceptions import CloudQueueError, MessageProcessingError
from .base import QueueClient

class AzureQueueClient(QueueClient):
    def __init__(self, connection_string, queue_name):
        try:
            self.client = AzureQueueClientSDK.from_connection_string(
                conn_str=connection_string, queue_name=queue_name
            )
        except Exception as e:
            raise CloudQueueError(f"Failed to connect to Azure Queue: {e}") from e

    def receive_messages(self, messages_per_page=1, visibility_timeout=30, wait_time=10):
        try:
            return self.client.receive_messages(
                messages_per_page=messages_per_page,
                visibility_timeout=visibility_timeout
            )
        except Exception as e:
            raise CloudQueueError(f"Failed to receive messages from Azure Queue: {e}") from e

    def delete_message(self, message):
        try:
            self.client.delete_message(message.id, message.pop_receipt)
        except Exception as e:
            raise MessageProcessingError(f"Failed to delete message: {e}") from e

    def send_message(self, message_body, encode_json=False, **kwargs):
            """
            Add a message to the Azure Queue.
            :param message_body: String or dict (if encode_json=True)
            :param encode_json: If True, serializes Python dict to JSON
            :param kwargs: Additional keyword args for Azure SDK send_message
            :return: Response from Azure SDK
            """
            try:
                if encode_json and isinstance(message_body, dict):
                    message_body = json.dumps(message_body)
                return self.client.send_message(message_body, **kwargs)
            except Exception as e:
                raise CloudQueueError(f"Failed to send message to Azure Queue: {e}") from e