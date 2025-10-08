import time

def receive_forever(queue_client, handler, poll_interval=1,
                    messages_per_page=1, visibility_timeout=30, wait_time=10):
    """
    Continuously poll the queue and process messages using a handler.

    Args:
        queue_client: QueueClient instance (AWS/Azure/etc.)
        handler: function(message) -> bool (True if processed successfully)
        poll_interval: delay between polls when no messages are found
    """
    while True:
        messages = queue_client.receive_messages(
            messages_per_page=messages_per_page,
            visibility_timeout=visibility_timeout,
            wait_time=wait_time,
        )

        if not messages:
            time.sleep(poll_interval)
            continue

        for msg in messages:
            try:
                success = handler(msg)
                if success:
                    queue_client.delete_message(msg)
            except Exception as e:
                print(f"Error processing message: {e}")