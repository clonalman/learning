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
    mutation {
      notify(message: {
        id: 200
        title: "闻泰科技05月18日被沪股通减持244.5万股"
        author: "东方财富网"
        url: "https://stock.eastmoney.com/a/202205192384190436.html"
        summary: "05月18日，闻泰科技被沪股通减持244.5万股，已连续6日被沪股通减持，共计788.91万股，最新持股量为5712.74万股，占公司A股总股本的4.58%。"
        date_updated: "2022-05-18T01:59:39.000Z"
        date_created: "2022-05-18T01:59:38.000Z"
        topics: ["股票"]
        tags: ["闻泰科技"]
      })
    }
    """
)

# Execute the query on the transport
result = client.execute(query)
print(result)