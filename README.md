# athena-assetnote

## Introduction
Scripts to interact with Assetnote portal for asset discovery

## Notes:
* URL Format in the Assetnote script is as follows:
https://urldefense.proofpoint.com/v2/url?u=https-3A__-257B0-257D.assetnotecloud.com_api_v2_graphql-2522.format-28INSTANCE-29&d=DwIGAg&c=8bHjhITO0F85Cmi91C_4TA&r=QqfjnWA9BCxy5l6XlPCZsA2vjEkeSJcRyCWM1o_rcwk&m=vfNmfalqF6Up6dMPcBgZXtVxWC5e4HRbxPU1gfcHhU4&s=kVhc1vpZ4e-QBAAdADhlXqFG94SWOAAIInS8NB3AlBw&e=
```
"https://{}.assetnotecloud.com/api/v2/graphql".format(INSTANCE)
```
* For building Assetnote Graphql searches, utilize the 'Network' tab in Chrome to see what queries is being made by the website.
* Working query:

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
