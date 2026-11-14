#!/bin/sh
# Download every golf feature around Fox Hollow Golf Club (Branchburg NJ,
# course boundary = OSM way 40419138) into data/osm_raw.json.
# Uses a bounding box with ~200 m margin rather than the boundary polygon,
# because hole 16's green is mapped just outside the boundary.
# Then run: python scripts/build_course.py
set -e
cd "$(dirname "$0")/.."
mkdir -p data
BBOX='40.6100,-74.7145,40.6245,-74.6965'
curl -s -A "golf-course-viewer" --data-urlencode "data=[out:json][timeout:120];(way(40419138);way[\"golf\"]($BBOX);node[\"golf\"]($BBOX);relation[\"golf\"]($BBOX);way[\"natural\"=\"water\"]($BBOX);relation[\"natural\"=\"water\"]($BBOX););out geom;" \
  https://overpass-api.de/api/interpreter -o data/osm_raw.json
echo "saved data/osm_raw.json"
