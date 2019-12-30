import json
import requests
import os

YOUR_API_KEY = "INSERT YOUR API KEY HERE"
INSTANCE = "YOUR INSTANCE"

os.makedirs(INSTANCE.replace("-", "_"), exist_ok=True)

asset_query = """query {{
  assets(s:[{{
    rel:"assetGroup",
    field:"name",
    dir:ASC
  }}],count:100,page:{0}) {{
    edges {{
      node {{
          ... on BaseAsset {{
              humanName
        assetGroup {{
          name
        }}
        }}
      }}
    }}
  }}
}}"""

asset_edges = []

total = None
page = 0

while total is None or total == 100:
    x = requests.post(
        "https://urldefense.proofpoint.com/v2/url?u=https-3A__-257B0-257D.assetnotecloud.com_api_v2_graphql-2522.format-28INSTANCE-29&d=DwIGAg&c=8bHjhITO0F85Cmi91C_4TA&r=QqfjnWA9BCxy5l6XlPCZsA2vjEkeSJcRyCWM1o_rcwk&m=vfNmfalqF6Up6dMPcBgZXtVxWC5e4HRbxPU1gfcHhU4&s=kVhc1vpZ4e-QBAAdADhlXqFG94SWOAAIInS8NB3AlBw&e= ,
        headers={
            "X-ASSETNOTE-API-KEY":YOUR_API_KEY
        },
        json=dict(query=asset_query.format(page))
    ).json()

    nodes = x["data"]["assets"]["edges"]

    total = len(nodes)
    print("Got page {0} of assets (total: {1}, so far: {2})".format(page, total, len(asset_edges)))

    page = page+1

    asset_edges = asset_edges + nodes


by_ag = dict()
for asset in asset_edges:
    ag_key = asset["node"]["assetGroup"]["name"]
    if ag_key not in by_ag.keys():
        by_ag[ag_key] =  []
    by_ag[ag_key].append(asset["node"]["humanName"])

for k, v in by_ag.items():
    open("{0}/{1}-assets.txt".format(INSTANCE.replace("-", "_"), k), "w").write("\n".join(v))

print("Saved {0} assets".format(len(asset_edges)))

domain_query = """query {{
  domains(s:[{{
    rel:"assetGroup",
    field:"name",
    dir:ASC
  }}],count:100,page:{0}) {{
    edges {{
      node {{
        name
        assetGroup {{
          name
        }}
      }}
    }}
  }}
}}"""

domain_edges = []

total = None
page = 0

while total is None or total == 100:
    x = requests.post(
        "https://urldefense.proofpoint.com/v2/url?u=https-3A__-257B0-257D.assetnotecloud.com_api_v2_graphql-2522.format-28INSTANCE-29&d=DwIGAg&c=8bHjhITO0F85Cmi91C_4TA&r=QqfjnWA9BCxy5l6XlPCZsA2vjEkeSJcRyCWM1o_rcwk&m=vfNmfalqF6Up6dMPcBgZXtVxWC5e4HRbxPU1gfcHhU4&s=kVhc1vpZ4e-QBAAdADhlXqFG94SWOAAIInS8NB3AlBw&e= ,
        headers={
            "X-ASSETNOTE-API-KEY":YOUR_API_KEY
        },
        json=dict(query=domain_query.format(page))
    ).json()

    nodes = x["data"]["domains"]["edges"]

    total = len(nodes)
    print("Got page {0} of domains (total: {1}, so far: {2})".format(page, total, len(domain_edges)))

    page = page+1

    domain_edges = domain_edges + nodes


by_ag = dict()

for domain in domain_edges:
    ag_key = domain["node"]["assetGroup"]["name"]
    if ag_key not in by_ag.keys():
        by_ag[ag_key] =  []
    by_ag[ag_key].append(domain["node"]["name"])

for k, v in by_ag.items():
    open("{0}/{1}.txt".format(INSTANCE.replace("-", "_"), k), "w").write("\n".join(v))

print("Saved {0} assets".format(len(domain_edges)))
