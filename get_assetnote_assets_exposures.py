#!/usr/bin/env python3
import argparse
import json
import requests
import time

# Graph Query templates to pull vulnerability and indicators
EXPOSURES_GRAPHQL_QUERY_TEMPLATE = """
query {{
    exposures(count:{page_count},page:{page_num}) {{
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
                        ... on HTTPSignature {{
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

# Graphql Query template to pull down assets. {page_count} is set and {page_num} is incremented
# to pull down the assets listing
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
                        ipAddress,
                        technologies {{
                            edges {{
                                node {{
                                    name
                                }}
                            }}
                        }},
                        services {{
                            edges {{
                                node {{
                                    name,
                                    port,
                                    isActive,
                                    lastActive
                                }}
                            }}
                        }}
                    }},
                    ... on CloudAsset {{
                        ipAddress,
                        technologies {{
                            edges {{
                                node {{
                                    name
                                }}
                            }}
                        }},
                        services {{
                            edges {{
                                node {{
                                    name,
                                    port,
                                    isActive,
                                    lastActive
                                }}
                            }}
                        }}
                    }},
                    ... on SubdomainAsset {{
                       ipAddress,
                       technologies {{
                            edges {{
                                node {{
                                    name
                                }}
                            }}
                        }},
                        services {{
                            edges {{
                                node {{
                                    name,
                                    port,
                                    isActive,
                                    lastActive
                                }}
                            }}
                        }}
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
    if 'verbose' in args:
        print("[*] " + msg.format(**args))

def error(args, msg):
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

def sleep_time(args):
    """
    Sleep and let the user know that we are sleeping before making requests

    Arguments
    ---------
    args: dict
        Arguments provided by the user including sleep time
    """
    if 'sleep_time' in args:
        sleep_time = int(args['sleep_time'])
        info(args, "Sleeping for {sleep_time}s...".format(**args))
        time.sleep(sleep_time)

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
    parser.add_argument("-sa", "--skip-assets", action="store_true",
                        help="Skip assets export")
    parser.add_argument("-se", "--skip-exposures", action="store_true",
                        help="Skip exposures export")
    parser.add_argument("-st", "--sleep-time", action="store", default="2",
                        help="Sleep timeout between individual requests")
    args = vars(parser.parse_args())
    
    info(args, "Validing the value of 'limit_pages_returned' argument...")
    try:
        args['limit_pages_returned'] = int(args['limit_pages_returned'])
    except:
        error(args, "Invalid value for limit pages returned provided, defaulting to 0...")
        args['limit_pages_returned'] = 0

    if not args['skip_assets']:

        info(args, "Requesting assets for instance: {instance} page-wise...")
        assets = []
        get_next_page = True
        args['page_num'] = 1
        while get_next_page:
            
            info(args, "Requesting page: {page_num} for assets...")
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
    
                info(args, "Checking if page: {page_num} obtained successfully...")
                if status_code != 200 or 'data' not in resp_json:
                    error(args, "Error encountered when retrieving page: {page_num}...")
                    error(args, "Error: ")
                    print(json.dumps(resp_json, indent=4))
                    get_next_page = False
    
                else:
    
                    info(args, "Parsing page: {page_num} response for assets...")
                    
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
    
                error(args, "Error encountered when requesting page: {page_num} for assets...")
                error(args, str(e))
                get_next_page = False
    
            info(args, "Writing assets to outfile: {outfile_assets}")
            with open(args['outfile_assets'], "w+") as f:
                f.write(json.dumps(assets, indent=4))
            
            sleep_time(args)
    else:
        info(args, "Skipping assets export as requested by user when invoking the script...")

    if not args['skip_exposures']:

        info(args, "Requesting exposures for instance: {instance} page-wise...")
        exposures = []
        get_next_page = True
        args['page_num'] = 1
        while get_next_page:
            
            info(args, "Requesting page: {page_num} for exposures...")
            graphql_query = EXPOSURES_GRAPHQL_QUERY_TEMPLATE.format(**args)
            try:
                resp = requests.post(
                            "https://{instance}.assetnotecloud.com/api/v2/graphql".format(**args),
                            headers={
                                "X-ASSETNOTE-API-KEY": "{api_key}".format(**args)
                            }, json=dict(query=graphql_query)
                )
                status_code = resp.status_code
                resp_json = resp.json()
                
                info(args, "Checking if page: {page_num} obtained successfully...")
                if status_code != 200 or "errors" in resp_json:
                    error(args, "Error encountered when retrieving page: {page_num} for exposures...")
                    error(args, "Error: ")
                    print(json.dumps(resp_json, indent=4))
                    get_next_page = False
    
                else:
    
                    info(args, "Parsing page: {page_num} respons for exposurese...")
    
                    info(args, "Getting exposures from the page...")
                    assets_on_page = resp_json['data']['exposures']['edges']
                    for asset_on_page in assets_on_page:
                        exposures.append(asset_on_page)
                        args['exposures_count'] = len(exposures)
                    info(args, "Number of assets after page: {page_num} is: {exposures_count}")
    
                    info(args, "Checking if another page exists from page: {page_num} response...")
                    get_next_page = resp_json['data']['exposures']['pageInfo']['hasNextPage']
                    if get_next_page:
                        args['page_num'] += 1
                        if args['limit_pages_returned'] > 0:
                            if int(args['page_num']) > args['limit_pages_returned']:
                                info(args, "Stopping extraction of more pages as limit of number of pages to get hit...")
                                get_next_page = False
    
            except Exception as e:
    
                error(args, "Error encountered when requesting page: {page_num} for exposures...")
                error(args, str(e))
                get_next_page = False
    
            info(args, "Writing exposures to outfile: {outfile_exposures}")
            with open(args['outfile_exposures'], "w+") as f:
                f.write(json.dumps(exposures, indent=4))
            
            sleep_time(args)

    else:
        info(args, "Skipping assets as requested by user when invoking the script...")


if __name__ == "__main__":
    main()

