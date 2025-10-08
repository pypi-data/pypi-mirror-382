from functools import partial
from multi_cloud_queue import QueueClientFactory

def my_processor(message, db_conn, custom_delay):
    print("Processing:", message)
    print("DB Connection:", db_conn)
    print("Custom Delay:", custom_delay)

# Example usage with AWS
aws_client = QueueClientFactory.create_client(
    "aws", queue_name="my-queue", region="us-east-1"
)

# pre-fill db_conn and custom_delay
processor_with_args = partial(my_processor, db_conn="mysql://localhost", custom_delay=5)

aws_client.receive_forever(
    process_message=processor_with_args,
    messages_per_page=2,
    visibility_timeout=60,
    wait_time=10
)