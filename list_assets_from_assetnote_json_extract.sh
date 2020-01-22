#!/bin/bash
# 
# This script will extract all the assets from the out-assetnote-assets.json file
cat out-assetnote-assets.json | \
    jq -r ".[].node.host" out-assetnote-assets.json | \
    sort | \
    uniq
