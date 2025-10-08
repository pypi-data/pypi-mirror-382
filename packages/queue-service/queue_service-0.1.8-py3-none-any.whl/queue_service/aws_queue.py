# cloudqueue/queues/aws_queue.py
import boto3
import uuid
from botocore.exceptions import BotoCoreError, ClientError
from .exceptions import CloudQueueError, MessageProcessingError
from .base import QueueClient

class AWSQueueClient(QueueClient):
    def __init__(self, queue_name, region_name="us-east-1"):
        try:
            self.sqs = boto3.resource("sqs", region_name=region_name)
            self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)
        except (BotoCoreError, ClientError) as e:
            raise CloudQueueError(f"Failed to connect to AWS SQS: {e}") from e

    def receive_messages(self, messages_per_page=1, visibility_timeout=30, wait_time=10):
        try:
            return self.queue.receive_messages(
                MaxNumberOfMessages=messages_per_page,
                VisibilityTimeout=visibility_timeout,
                WaitTimeSeconds=wait_time
            )
        except (BotoCoreError, ClientError) as e:
            raise CloudQueueError(f"Failed to receive messages from AWS SQS: {e}") from e

    def delete_message(self, message) -> bool:
        try:
            message.delete()
            return True  # ✅ deletion successful
        except Exception as e:
            print(f"❌ Failed to delete message: {e}")
            return False  # ❌ deletion failed

    def send_message(self, message_body, message_attributes=None, delay_seconds=0):
        """
        Send a message to the SQS queue.

        :param message_body: The body of the message (string)
        :param message_attributes: Optional dict of attributes
        :param delay_seconds: Optional delay in seconds before message is available
        :return: Response from SQS
        """
        try:
            kwargs = {
                "MessageBody": message_body,
                "MessageAttributes": message_attributes or {},
                "DelaySeconds": delay_seconds
            }

            # Add FIFO parameters if queue is FIFO
            if self.queue.url.endswith(".fifo"):
                kwargs["MessageGroupId"] = "FHIR_GROUP"  # or dynamic per message
                kwargs["MessageDeduplicationId"] = str(uuid.uuid4())

            return self.queue.send_message(**kwargs)
        except (BotoCoreError, ClientError) as e:
            raise CloudQueueError(f"Failed to send message to AWS SQS: {e}") from e
