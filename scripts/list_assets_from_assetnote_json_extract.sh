#!/bin/bash
# 
# This script will extract all the assets from the out-assetnote-assets.json file
# 
if [ $# -lt 1 ]; then
    echo "[*] $0 run [assets-json-file=out-assetnote-assets.json] [outfile=out-assetnote-assets.csv]"
    exit
fi
assets_json_file=${1:-"out-assetnote-assets.json"}
outfile=${2:-"out-assetnote-assets.csv"}

echo "[*] Parsing input assets from: $assets_json_file and writing assets to outfile: $outfile..."
jq -r ".[].node.host" "$assets_json_file" | \
    sort | \
    uniq | \
    tee "$outfile"

