#!/usr/bin/env python3
import argparse
import json
import requests
import os
import sys


parser = argparse.ArgumentParser(description="Script to test Assetnote GrahQL API")
parser.add_argument("-i", "--instance", required=True,
                    help="Instance of AssetNote to connect to")
parser.add_argument("-k", "--api-key", required=True, 
                    help="API Key for AssetNote to connect to")
args = parser.parse_args()
INSTANCE = args.instance
YOUR_API_KEY = args.api_key

print(args)

os.makedirs(INSTANCE.replace("-", "_"), exist_ok=True)
#
#asset_query = """query {{
#  assets(s:[{{
#    rel:"assetGroup",
#    field:"name",
#    dir:ASC
#  }}],count:100,page:{0}) {{
#    edges {{
#      node {{
#          ... on BaseAsset {{
#              humanName
#        assetGroup {{
#          name
#        }}
#        }}
#      }}
#    }}
#  }}
#}}"""
#
#asset_edges = []
#
#total = None
#page = 0
#
#while total is None or total == 100:
#    x = requests.post(
#        "https://{}.assetnotecloud.com/api/v2/graphql".format(INSTANCE),
#        headers={
#            "X-ASSETNOTE-API-KEY":YOUR_API_KEY
#        },
#        json=dict(query=asset_query.format(page))
#    ).json()
#
#    nodes = x["data"]["assets"]["edges"]
#
#    total = len(nodes)
#    print("Got page {0} of assets (total: {1}, so far: {2})".format(page, total, len(asset_edges)))
#
#    page = page+1
#
#    asset_edges = asset_edges + nodes
#
#
#by_ag = dict()
#for asset in asset_edges:
#    ag_key = asset["node"]["assetGroup"]["name"]
#    if ag_key not in by_ag.keys():
#        by_ag[ag_key] =  []
#    by_ag[ag_key].append(asset["node"]["humanName"])
#
#for k, v in by_ag.items():
#    open("{0}/{1}-assets.txt".format(INSTANCE.replace("-", "_"), k), "w").write("\n".join(v))
#
#print("Saved {0} assets".format(len(asset_edges)))
#
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

print(domain_query)

domain_edges = []

total = None
page = 0

while total is None or total == 100:
    x = requests.post(
        "https://{}.assetnotecloud.com/api/v2/graphql".format(INSTANCE),
        headers={
            "X-ASSETNOTE-API-KEY":YOUR_API_KEY
        },
        json=dict(query=domain_query.format(page))
    ).json()

    print(x)

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
