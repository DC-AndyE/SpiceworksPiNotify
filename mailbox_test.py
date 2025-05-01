import asyncio
from graph_client_builder import get_graph_client
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.models.o_data_errors.o_data_error import ODataError

async def test_mailbox_access(email_address: str):
    graph_client = get_graph_client()

    try:
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=["subject"],
            top=1,
            orderby=["receivedDateTime desc"]
        )

        request_config = RequestConfiguration(query_parameters=query_params)

        result = await graph_client.users.by_user_id(email_address).messages.get(request_configuration=request_config)

        if result and result.value:
            print(f"✅ SUCCESS: Access granted to {email_address}")
            for msg in result.value:
                print(f"  Subject: {msg.subject}")
        else:
            print(f"ℹ️ No messages found for {email_address}, but access appears valid.")

    except ODataError as e:
        if e.error and e.error.code == 'ErrorAccessDenied':
            print(f"❌ ACCESS DENIED: Cannot access {email_address}")
        else:
            print(f"❌ API ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_mailbox_access("pi-spiceworks@denstonecollege.net"))
