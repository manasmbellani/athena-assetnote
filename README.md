# athena-assetnote: Assetnote App for Splunk

## Introduction
This project contains scripts to interact with Assetnote portal for asset discovery and exposures/indicators.

It also contains instructions on how to setup and install the Assetnote TA which uses this script in the background to pull down GraphQL data.

Currently, this add-on pulls the following data from Assetnoe UI console into different Sourcetypes within Splunk:
* Assets
    * Subdomain
    * IPs
* Exposures
* Asset Groups
    * Domains
    * IPs

## Setup for using scripts (not Technical add-on)

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
The following is a list of scripts available in this repository:

### get_assetnote_assets_exposures.py

This script currently allows users to pull down assets and exposures in the given assetnote instance. 

To run the script, use the following command:

```
./get_assetnote_assets_exposures.py -lp 3 -i <instance-name> -ak <api-key>
```

Note that:

* This will pull the first 3 pages of assets. To pull down all pages and all results, run `-lp 0` or omit `-lp` option altogether.
* By default, the assets are written to the output file: `out-assetnote-assets.json` and the exposures are written to output file: `out-assetnote-exposures.json`

* `<instance-name>` is typically the company name

### list_assets_from_assetnote_json_extract.sh

This script will read the JSON output of `./get_assetnote_assets_exposures.py` above and extract the list of all unique domains as a single list into an output CSV file.

Example usage which reads the `out-assetnote-assets.json` file from a user and writes the output to `out-assetnote-asset.csv` file

```
./list_assets_from_assetnote_json_extract.sh out-assetnote-assets.json out-assetnote-assets.csv
```

## Splunk Add-On for AssetNote

### Introduction

A Splunk Technology add-on for Assetnote has been created using the Splunk Add-On Builder app from Splunk Marketplace.

This Add-On communicates with Assetnote Cloud environment on a regular basis and collects information about all configured assets, and exposures from .

CIM compliance has also been performed for field mappings within the Assetnote TA through the Splunk add-on builder app.

### Pre-requisites
The pre-requsites for this add-on are as follows:
* The splunk instance on which the add-on is installed should be able to visit domain: `<assetnote-instance>.assetnotecloud.com` on port 443. So, if the assetnote instance is hosted on `demo.assetnotecloud.com`, the instance should be able to communicate on port 443.
* The Assetnote API key obtained from the Assetnote UI console.

### How it works?

By Default, this Splunk add-on will connect to the Assetnote's GraphQL API to pull down assets and exposures info in JSON fromat on a frequency configured by the operator in a paginated fashion. The maximum page size by default is `20`. 

The results are by default written to `assetnote_index` and the `.json` source types mentioned in sections below for exposures and assets.

The Add-on will add each page of data retrieved as a single event, but default Splunk `json` setting may break each event into smaller, individual events. 

### Splunk Add-On Installation

#### Installing the Spunk Dev Environment (Optional)

To setup the dev environment, we do this via the Splunk Docker container which will run a Splunk environment locally on our system.

If you already have a live Splunk Instance, you can skip to the next section.

The steps to setup the environment are taken from [here](https://hub.docker.com/r/splunk/splunk/#Quickstart). These are as follows:

* Pull Docker image

```
docker pull splunk/splunk:latest
```

* Build the container with password `Splunk123$`

```
docker run -v /opt/athena-assetnote:/opt/athena-assetnote -d -p 8000:8000 -e "SPLUNK_START_ARGS=--accept-license" -e "SPLUNK_PASSWORD=Splunk123$" --name splunk splunk/splunk:latest
```

Splunk instance should now be available locally on the host at address: `http://127.0.0.1:8000` with default login `admin:Splunk123$`.

#### Install Splunk Add-On

* Obtain the latest copy of the Assetnote add-on from [here](https://github.com/manasmbellani/athena-assetnote/releases)
* Install the Assetnote add-on by visiting `Apps: Drop-Down > Manage Apps > Install App from File`

#### Index Definition

* Now, create an index called: `assetnote_index` in Splunk from `Settings > Indexes` with default settings - this can be created in any app although it is recommended to create it within this TA.

#### Sourcetypes Definition

* Create a sourcetype from `Settings > Source Types` called: `assetnote:assets:json2` in Splunk and set the sourcetype `Indexed Extraction` field to `none`.
* Ensure a new field called `KV_MODE` key is added in `Advanced`, and set to `json` to extract fields on searchtime.

* Create a sourcetype from `Settings > Source Types` called: `assetnote:exposures:json2` in Splunk and set the sourcetype `Indexed Extraction` field to `none`.
* Ensure a new field called `KV_MODE` key is added in `Advanced`, and set to `json` to extract fields on searchtime.

* Create a sourcetype from `Settings > Source Types` called: `assetnote:assetgroups:json2` in Splunk and set the sourcetype `Indexed Extraction` field to `none`.
* Ensure a new field called `KV_MODE` key is added in `Advanced`, and set to `json` to extract fields on searchtime.

#### Configuring Assetnote Add-On

* Now visit the *Assetnote Add-On* page from the `Apps` drop-down.

* Now `Create a New Input` called `Assetnote Graphql Input Python Script for Assets Collection`  for collecting Assets into Splunk.

    * Enter the following details for the form provided:
        * Name: `assetnote_python_assets_script`
        * Interval: `21600`. This is the frequency (in seconds) with which data collection should occur.
        * Index: `assetnote_index`
        * Assetnote Instance: `<instance-name-eg-demo>`
        * Assetnote API Key: `ugwqx........==`. This is the API key used for Assetnote.

* Now `Create a New Input` called `Assetnote Graphql Input Python Script for Exposures Collection`  for collecting Exposures into Splunk.

    * Enter the following details for the form provided:
      * Name: `assetnote_python_exposures_script`
      * Interval: `21600` . This is the frequency (in seconds) with which data collection should occur.
      * Index: `assetnote_index`
      * Assetnote Instance: `<instance-name-eg-demo>`
      * Assetnote API Key: `ugwqx........==`. This is the API key used for Assetnote.

* Now `Create a New Input` called `Assetnote Graphql Input Python Script for Assetgroups Collection`  for collecting Assetgroups and its assets into Splunk.

    * Enter the following details for the form provided:
      * Name: `assetnote_python_assetgroups_download`
      * Interval: `21600` . This is the frequency (in seconds) with which data collection should occur.
      * Index: `assetnote_index`
      * Assetnote Instance: `<instance-name-eg-demo>`
      * Assetnote API Key: `ugwqx........==`. This is the API key used for Assetnote.

* Enable both data inputs 

    * Once completed, info will flow into index: `assetnote_index` and sourcetype: `assetnote:assets:json2` for assets, `assetnote:exposures:json2` for exposures and `assetnote:assetgroups:json2` for assetgroups and their assets (domains, IP ranges)

* Run the following search to view the assetnote data:

    ```
    index=assetnote_index
    ```

## Appendix

This section contains misc information useful for development purposes. 

It can be ignored by the consumers of the scripts and add-on.

### Handy Search to see logs when building the Assetenote Add-on

```
index=_internal sourcetype="*assetnote*"
```

### Opening source files via TextEdit

```
open -a TextEdit test.txt
```



### Example of Working GraphQL query

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
