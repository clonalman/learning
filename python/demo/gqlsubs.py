from gql import gql, Client
from gql.transport.websockets import WebsocketsTransport

transport = WebsocketsTransport(
    url="ws://sfc.leadsant.com/subscriptions",
    headers={
        "graphql-user": "admin",
        "graphql-secret": "$2a$10$cVlyVY05q3h.5T8bV4qJP.ZrAbgwzsf8FIEdb8LXfDnaIMEDfxAEy",
        "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
        "Sec-WebSocket-Protocol": "graphql-ws"
    })

client = Client(
    transport=transport,
    fetch_schema_from_transport=False,
)

query = gql(
    """
    subscription {
      notify(filter: { topics: ["股票"], tags: ["闻泰科技"] })
    }
    """
)

for result in client.subscribe(query):
    print (result)