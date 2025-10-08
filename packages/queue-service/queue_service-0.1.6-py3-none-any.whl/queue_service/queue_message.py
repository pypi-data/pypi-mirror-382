import json

class QueueMessage:
    def __init__(self, provider, original_message):
        self.provider = provider  # 'aws' or 'azure'
        self.original_message = original_message
        # decode JSON body
        self.body = json.loads(original_message.body) if provider == 'aws' else json.loads(original_message.content)
        # store receipt handle or message ID for deletion
        self.id = getattr(original_message, 'receipt_handle', None) or getattr(original_message, 'id', None)