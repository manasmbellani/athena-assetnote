# encoding = utf-8

import json
import os
import sys
import time
import datetime

"""Sleep time between individual page loads (per page to load)"""
SLEEP_TIMEOUT_PER_PAGE = 2

"""Special prefix added to each log message"""
LOG_PREFIX = "AssetNote"

"""Number of exposures to load per page"""
EXPOSURES_PER_PAGE_COUNT = 20

"""Limit the number of pages returned with exposures (for testing)"""
LIMIT_PAGES_RETURNED = 1

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

def info(helper, all_params, msg, format_params=True):
    
    """"
    Write amn info log message
    
    Arguments
    ---------
    helper: helper
        Helper for splunk
    all_params: dict
        Parameters to substitute in the message to print
    msg: str
        Info message to print to the internal log
    format_params: bool
        Format the parameters out in the original message
    """
    msg_to_log = LOG_PREFIX + ":INFO: " + msg
    if format_params:
        helper.log_debug(msg_to_log.format(**all_params))
    else:
        helper.log_debug(msg_to_log)
        
'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    pass

def collect_events(helper, ew):
    opt_assetnote_api_key = helper.get_arg('assetnote_api_key')
    opt_assetnote_instance = helper.get_arg('assetnote_instance')
    
    all_params = {'assetnote_index': helper.get_output_index(),
                  'assetnote_sourcetype': helper.get_sourcetype(),
                  'assetnote_source': helper.get_input_type(),
                  'assetnote_api_key': opt_assetnote_api_key,
                  'assetnote_instance': opt_assetnote_instance,
                  'sleep_time': SLEEP_TIMEOUT_PER_PAGE,
                  'page_count': EXPOSURES_PER_PAGE_COUNT,
                  'limit_pages_returned': LIMIT_PAGES_RETURNED}
    
    # Printing all the current parameters to internal log
    msg = ("assetnote_index: {assetnote_index},"
           "assetnote_sourcetype: {assetnote_sourcetype},"
           "assetnote_api_key: {assetnote_api_key},"
           "assetnote_instance: {assetnote_instance}")
    info(helper, all_params, msg)

    info(helper, all_params,
         "Requesting exposures for instance: {assetnote_instance} page-wise...")
    exposures = []
    get_next_page = True
    all_params['page_num'] = 1
    
    while get_next_page:

        info(helper, all_params, 
             "Requesting page: {page_num} for exposures from AssetNote...")
        graphql_query = EXPOSURES_GRAPHQL_QUERY_TEMPLATE.format(**all_params)
        url_to_call = "https://{assetnote_instance}.assetnotecloud.com/api/v2/graphql".format(**all_params)
        method = "POST"
        headers={
            "X-ASSETNOTE-API-KEY": "{assetnote_api_key}".format(**all_params)
        }
        payload = dict(query=graphql_query)
        resp = helper.send_http_request(url=url_to_call,
                                        method=method, 
                                        payload=payload,
                                        headers=headers,
                                        verify=True)
        
        info(helper, all_params, 
             "Parsing response from page: {page_num} from AssetNote...")
        status_code = resp.status_code
        resp_json = resp.json()

        info(helper, all_params,
            "Checking if page: {page_num} obtained successfully...")
        if status_code != 200 or "data" not in resp_json:
            
            info(helper, all_params, "Error encountered when retrieving page: {page_num}...")
            info(helper, all_params, "Error: ")
            info(helper, all_params,
                 str(resp_json), format_params=False)
            get_next_page = False
            
        else:

            info(helper, all_params,
                 "Parsing page: {page_num} response for exposures...")
                
            #info(helper, all_params, str(resp_json),
            #     format_params=False)
            
            info(helper, all_params, 
                "Listing the number of exposures on the page obtained...")
            exposures_on_page = resp_json['data']['exposures']['edges']
            for exposure_on_page in exposures_on_page:
                exposures.append(exposure_on_page)
                all_params['exposures_count'] = len(exposures)
                
            info(helper, all_params, 
                "Number of exposures after page: {page_num} is: {exposures_count}")

            info(helper, all_params,
                "Checking if another page exists from page: {page_num} response...")
                
            info(helper, all_params, 
                 "Calculating the number of exposures in the page...")
            all_params['exposure_count_per_page'] = len(exposures_on_page)
            
            info(helper, all_params, 
                 "Creating all {exposure_count_per_page} exposures as an event...")
            new_event = helper.new_event(json.dumps(exposures_on_page, indent=4),
                            index=all_params['assetnote_index'],
                            sourcetype=all_params['assetnote_sourcetype'],
                            source=all_params['assetnote_source'])
                            
            info(helper, all_params, 
                 "Writing an event to Splunk index: {assetnote_index}, sourcetype: {assetnote_sourcetype}, source: {assetnote_source}...")
            ew.write_event(new_event)
            
            
            info(helper, all_params, 
                    "Checking if next page should be obtained...")
            get_next_page_in_resp = resp_json['data']['exposures']['pageInfo']['hasNextPage']
            if get_next_page_in_resp:
                
                info(helper, all_params, 
                    "Checking if limit of number of pages to return has been hit...")
                if all_params['limit_pages_returned'] > 0:
                    if int(all_params['page_num']) >= all_params['limit_pages_returned']:
                        
                        info(helper, all_params, 
                            "Limit hit! Stopping extraction of more pages...")
                        get_next_page = False
            else:
                
                info(helper, all_params, 
                    "Stopping as no indication if next page is available...")
                get_next_page = False
                    
            if get_next_page:
                
                info(helper, all_params, 
                     "Incrementing page counter...") 
                all_params['page_num'] += 1
                
                info(helper, all_params, 
                     "Sleeping for {sleep_time}s before requesting next page...")
                time.sleep(all_params['sleep_time'])

