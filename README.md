# athena-assetnote

## Introduction
This project contains scripts to interact with Assetnote portal for asset discovery and exposures/indicators.

It will also be used in near-future to collaborate on building a splunk TA to integrate Assetnote with Splunk.

## Setup

Build a Docker container which contains all the necessary dependencies eg python3, jq for running the scripts

To build the container from the Dockerfile, run the following commmands:
```
docker build -t athena-assetnote:latest .
```

Then run a container with the following command:
```
docker run -it -v /opt/athena-assetnote:/opt/athena-assetnote athena-assetnote /bin/bash
```


## Scripts
The following is a list of scripts available:

* `get_assetnote_assets_exposures.py`: This script currently allows users to pull down assets and exposures in the given assetnote instance. 

To run the script, use the following command:

```
./get_assetnote_assets_exposures.py -lp 3 -i <instance-name> -ak <api-key> 
```

Note that:
* This will pull the first 3 pages of assets. To pull down all pages and all results, run `-lp 0` or omit `-lp` option altogether.
* `<instance-name>` is typically the company name

## Appendix

### Notes:
* An example of Working GraphQL query:

```
query {{
    assets(s:[{{rel:"assetGroup", field:"name", dir:ASC}}],count:2,page:1) {{
        edges {{
            node {{
                ... on BaseAsset {{
                    humanName,
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
                    id,                                                                     
                    importance,                                                             
                    isMonitored,                                                            
                    lastUpdated,                                                            
                    notificationsEnabled,                                                   
                    parentName,                                                             
                    risk,                                                                   
                    verifiedStatus,                                                         
                    assetGroup {{
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
                    exposureUrl
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
```
