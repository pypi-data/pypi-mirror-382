class CloudQueueError(Exception):
    """Base exception for cloudqueue library."""

class MessageProcessingError(CloudQueueError):
    """Raised when a message fails to process."""