from .aws_queue import AWSQueueClient
from .azure_queue import AzureQueueClient
# from .queues.gcp_queue import GCPQueueClient  # add later if needed

def get_queue_client(provider: str, **kwargs):
    provider = provider.lower()

    if provider == "aws":
        # Only pass required params for AWSQueueClient
        queue_name = kwargs.get("queue_name")
        region_name = kwargs.get("region_name", "us-east-1")
        return AWSQueueClient(queue_name=queue_name, region_name=region_name)

    elif provider == "azure":
        # Only pass required params for AzureQueueClient
        connection_string = kwargs.get("connection_string")
        queue_name = kwargs.get("queue_name")
        return AzureQueueClient(connection_string=connection_string, queue_name=queue_name)

    else:
        raise ValueError(f"Unsupported provider: {provider}")