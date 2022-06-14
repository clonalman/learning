from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(
    url="http://sfc.leadsant.com/graphql",
    headers={
        "graphql-user": "admin",
        "graphql-secret": "$2a$10$cVlyVY05q3h.5T8bV4qJP.ZrAbgwzsf8FIEdb8LXfDnaIMEDfxAEy"
    })

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
    query {
        topics
    }
    """
)

# Execute the query on the transport
result = client.execute(query)
print(result)