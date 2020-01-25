#!/bin/bash
# 
# This script will extract all the assets from the out-assetnote-assets.json file
# 
if [ $# -lt 1 ]; then
    echo "[*] $0 run [assets-json-file=out-assetnote-assets.json]"
    exit
fi
assets_json_file="out-assetnote-assets.json"

jq -r ".[].node.host" "$assets_json_file" | \
    sort | \
    uniq
