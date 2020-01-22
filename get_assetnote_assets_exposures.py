#!/usr/bin/env python3
import argparse
import json
import requests

# Inputs
EXPOSURES_GRAPHQL_QUERY_TEMPLATE = """
query {{
    exposures(s:[{{field:"name", dir:ASC}}],count:{page_count},page:{page_num}) {{
        edges {{
            node {{
                ... on BaseExposure {{
                    id,
                    name,
                    exposureUrl,
                    isIgnored,
                    currentIncidentUuid,
                    lastDetected,
                    latestExposureEventType,
                    assetGroup,
                    category,
                    created,
                    definition,
                    lastUpdated,
                    probeId,
                    severity,
                    severityNormalized,
                    signature {{
                        ... on BaseExposureSiganture {{
                            categoryId,
                            categoryName,
                            created,
                            cve,
                            definitionName,
                            description,
                            enabled,
                            followRedirects,
                            hasTemplate,
                            lastUpdated,
                            name,
                            recommendations,
                            references,
                            severity,
                            signatureType,
                            definition {{
                                id,
                                name,
                                categoryId,
                                categoryName,
                                created,
                                description,
                                lastUpdated,
                                signatureCount
                            }}
                        }}
                    }}
                    asset {{
                        ... on SubdomainAsset {{
                            id,
                            host
                        }}
                    }}
                }}
            }}
        }},
        pageInfo {{
            hasNextPage,
            hasPreviousPage,
            startCursor,
            endCursor
        }}
    }}
}}
"""

ASSETS_GRAPHQL_QUERY_TEMPLATE = """
query {{
    assets(s:[{{rel:"assetGroup", field:"name", dir:ASC}}],count:{page_count},page:{page_num}) {{
        edges {{
            node {{
                ... on CloudAsset {{
                    activeARecords {{
                        edges {{
                            node {{ 
                                ... on ADnsRecord {{
                                    id,
                                    ipAddress
                                }}
                            }}
                        }}
                    }},
                    activeCnameRecords {{
                        edges {{
                            node {{
                                ... on CnameDnsRecord {{
                                    id,
                                    subdomain,
                                    rawRecord
                                }}
                            }}
                        }}
                    }}
                }},
                ... on IpAsset {{
                    activeARecords {{
                        edges {{
                            node {{ 
                                ... on ADnsRecord {{
                                    id,
                                    ipAddress
                                }}
                            }}
                        }}
                    }},
                    activeCnameRecords {{
                        edges {{
                            node {{
                                ... on CnameDnsRecord {{
                                    id,
                                    subdomain,
                                    rawRecord
                                }}
                            }}
                        }}
                    }}
                }},
                ... on SubdomainAsset {{
                    activeARecords {{
                        edges {{
                            node {{ 
                                ... on ADnsRecord {{
                                    id,
                                    ipAddress
                                }}
                            }}
                        }}
                    }},
                    activeCnameRecords {{
                        edges {{
                            node {{
                                ... on CnameDnsRecord {{
                                    id,
                                    subdomain,
                                    rawRecord
                                }}
                            }}
                        }}
                    }}
                }},
                __typename,
    	        ... on BaseAsset {{
                    humanName,
                    activeARecordCount,
        	    activeCnameRecordCount,
	            exposureRating,
            	    hasUnmanagedExposures,
	            activeARecordCount,
            	    onlinePortEntryCount,
                    isOnline,
	            onlineDnsEntryCount,
	            onlineTechnologyCount,
                    canBeMonitored,
	            assetGroupId,
	            assetGroupName,
	            assetType,
	            created,
	            geoData {{
                        id,
                        city,
                        country
                    }},
	            host,
                    ... on IpAsset {{
                        ipAddress
                    }},
                    ... on CloudAsset {{
                        ipAddress
                    }},
                    ... on SubdomainAsset {{
                       ipAddress 
                    }},
	            id,
	            importance,
 	            isMonitored,
    	            lastUpdated,
	            notificationsEnabled,
	            parentName,
	            risk,
	            verifiedStatus,
                    assetGroup {{
                        id,
                        name
                    }}
	        }}
            }}
        }},
        pageInfo {{
            hasNextPage,
            hasPreviousPage,
            startCursor,
            endCursor
        }}
    }},
    exposures {{
        edges {{
            node {{
                ... on BaseExposure {{
                    id,
                    name,
                    exposureUrl,
                    asset {{
                        ... on SubdomainAsset {{
                            id,
                            host
                        }}
                    }}
                }}
            }}
        }},
        pageInfo {{
            hasNextPage,
            hasPreviousPage,
            startCursor,
            endCursor
        }}
    }}
}}
"""

def info(args, msg):
    """
    Print an info message

    Arguments
    ---------
    args: dict
        Dictionary of params to sub in msg
    msg: str
        Message to print
    """
    print("[+] " + msg.format(**args))

def verbose(args, msg):
    """
    Print a verbose message when verbose flag set

    Arguments
    ---------
    args: dict
        Dictionary of params to sub in msg
    msg: str
        Message to print
    """
    if args['verbose']:
        print("[*] " + msg.format(**args))

def error(msg):
    """
    Print an error message

    Arguments
    ---------
    args: dict
        Dictionary of params to sub in msg
    msg: str
        Message to print as error
    """
    print("[-] " + msg.format(**args))

def main():
    parser = argparse.ArgumentParser(description="Script to pull down all assets and exposures in JSON and CSV format from Assetnote")
    parser.add_argument("-i", "--instance", required=True,
                        help="Instance ID for assetnote instance. The API URL is based on {{instance}}.assetnotecloud.com")
    parser.add_argument("-ak", "--api-key", required=True,
                        help="API key to use for downloading the exposures and assets listing")
    parser.add_argument("-oa", "--outfile-assets", default="out-assetnote-assets.json",
                        help="Output file containing assets listing")
    parser.add_argument("-oe", "--outfile-exposures", default="out-assetnote-exposures.json",
                        help="Output file containing exposures listing as a JSON output")
    parser.add_argument("-pc", "--page-count", default="20",
                        help="Number of items to provide per page count")
    parser.add_argument("-lp", "--limit-pages-returned", default=0,
                        help="Limit the number of pages returned. If set to 0 or less, no limit.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="More verbose Debugging output")
    args = vars(parser.parse_args())
    
    info(args, "Validing the value of 'limit_pages_returned' argument...")
    try:
        args['limit_pages_returned'] = int(args['limit_pages_returned'])
    except:
        error(args, "Invalid value for limit pages returned provided, defaulting to 0...")
        args['limit_pages_returned'] = 0

    info(args, "Requesting assets for instance: {instance} page-wise...")
    assets = []
    get_next_page = True
    args['page_num'] = 1
    while get_next_page:
        
        info(args, "Requesting page: {page_num}...")
        graphql_query = ASSETS_GRAPHQL_QUERY_TEMPLATE.format(**args)
        try:
            resp = requests.post(
                        "https://{instance}.assetnotecloud.com/api/v2/graphql".format(**args),
                        headers={
                            "X-ASSETNOTE-API-KEY": "{api_key}".format(**args)
                        }, json=dict(query=graphql_query)
            )
            status_code = resp.status_code
            resp_json = resp.json()

            with open('/tmp/test.json', 'w+') as f:
                f.write(
                        json.dumps(
                                resp_json, 
                                indent=4
                            ) 
                       )

            info(args, "Checking if page: {page_num} obtained successfully...")
            if status_code != 200 or "errors" in resp:
                error(args, "Error encountered when retrieving page: {page_num}...")
                error(args, "Error: ")
                json.dumps(resp_json, indent=4)
                get_next_page = False

            else:

                info(args, "Parsing page: {page_num} response...")

                
                info(args, "Getting assets from the page...")
                assets_on_page = resp_json['data']['assets']['edges']
                for asset_on_page in assets_on_page:
                    assets.append(asset_on_page)
                    args['assets_count'] = len(assets)
                info(args, "Number of assets after page: {page_num} is: {assets_count}")

                info(args, "Checking if another page exists from page: {page_num} response...")
                get_next_page = resp_json['data']['assets']['pageInfo']['hasNextPage']
                if get_next_page:
                    args['page_num'] += 1
                    if args['limit_pages_returned'] > 0:
                        if int(args['page_num']) > args['limit_pages_returned']:
                            info(args, "Stopping extraction of more pages as limit of number of pages to get hit...")
                            get_next_page = False


        except Exception as e:

            error(args, "Error encountered when requesting page: {page_num}")
            error(args, str(e))
            get_next_page = False

        info(args, "Writing assets to outfile: {outfile_assets}")
        with open(args['outfile_assets'], "w+") as f:
            f.write(json.dumps(assets, indent=4))

if __name__ == "__main__":
    main()

