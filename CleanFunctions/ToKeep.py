from time import time
from datetime import datetime
from .config import settings
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey


HOST = settings['host']
MASTER_KEY = settings['master_key']
DATABASE_ID = settings['database_id']
CONTAINER_ID = settings['container_id']

def get_container():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    db = client.get_database_client(DATABASE_ID)
    return db.get_container_client(CONTAINER_ID)

def get_last_records(container=None, minutesBack=60):
    """
    returns a list of dictionaries
    """
    timestamp_hour_ago = int((time()-minutesBack*60)*1000)
    print(f"time stamp now: {time()*1000}")
    print(f"time stamp hour ago: {timestamp_hour_ago}")

    if container is None:
        container = get_container()

    results = container.query_items(
        query= f'SELECT * FROM items WHERE (items["id"] >= "{timestamp_hour_ago}") order by items["id"] ASC',
        enable_cross_partition_query=True
    )
    # b=
    return list(results)
    


