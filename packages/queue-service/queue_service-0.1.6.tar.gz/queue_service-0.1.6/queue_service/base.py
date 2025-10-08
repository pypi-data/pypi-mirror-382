from abc import ABC, abstractmethod

class QueueClient(ABC):
    """Abstract base class for all queue clients."""

    @abstractmethod
    def receive_messages(self, messages_per_page=1, visibility_timeout=30, wait_time=10):
        """Fetch messages from the queue"""
        raise NotImplementedError

    @abstractmethod
    def delete_message(self, message):
        """Delete a message from the queue"""
        raise NotImplementedError