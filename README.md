# athena-assetnote

## Introduction
This project contains scripts to interact with Assetnote portal for asset discovery and exposures/indicators.

It will also be used in near-future to collaborate on building a splunk TA to integrate Assetnote with Splunk.

## Setup

Note that the instructions below assume that `athena-assetnote` has been git cloned in the `/opt` directory on a Linux host.

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

## Splunk Add-On for AssetNote (Under Development)
We are currently building a Splunk add-on for Assetnote while utilizing Splunk Add-On Builder app.

### Dev Environment Setup
To setup the dev environment, we do this via the Splunk Docker container which will run a Splunk environment locally on our system.

The steps to setup the environment are taken from [here](https://hub.docker.com/r/splunk/splunk/#Quickstart). These are as follows:

* Pull the Docker image

```
docker pull splunk/splunk:latest
```

* Build the container with password `Splunk123$`

```
docker run -v /opt/athena-assetnote:/opt/athena-assetnote -d -p 8000:8000 -e "SPLUNK_START_ARGS=--accept-license" -e "SPLUNK_PASSWORD=Splunk123$" --name splunk splunk/splunk:latest
```

### Splunk Add-On Steps
* Install the Assetnote addon

* Create an index called: `assetnote_index` in Splunk

* Create a sourcetype called: `assetnote:assets:json2` in Splunk and set the sourcetype `Indexed Extraction` field to `json`.

* Now configure a new input data collection in the Assetnote Add-On accessible from *Manage Apps* section

* Call it `assetnote_assets_python_script` and then configure the following: 
    * Interval: 120
    * Index: `assetnote_index`
    * Assetnote Instance: `<instance-name-eg-demo>`
    * Assetnote API Key: `ugwqx........==`

* Enable the Data Input

* Once completed, input will start coming into index: `assetnote_index` and sourcetype: `assetnote:assets:json`

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
