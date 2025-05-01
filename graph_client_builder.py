from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_graph_client():
    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    scopes = ['https://graph.microsoft.com/.default']

    graph_client = GraphServiceClient(credential, scopes)
    return graph_client
