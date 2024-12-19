#!/bin/bash

#
#  This bash script gets all workflows with their respective versions deployed in various vidarr instances
#

# Get the data
curl -s -X GET "https://vidarr-stage.gsi.oicr.on.ca/api/workflows" -H  "accept: application/json" > stage_workflows.json
curl -s -X GET "https://vidarr-clinical.gsi.oicr.on.ca/api/workflows" -H  "accept: application/json" > clinical_workflows.json
curl -s -X GET "https://vidarr-research.gsi.oicr.on.ca/api/workflows" -H  "accept: application/json" > research_workflows.json
# Dump everything into a file
cat stage_workflows.json | jq -r ' .[] | .name, .version' | paste - - | sort -u | awk '{print "STAGE\t"$0}' > vidarr_tags.tsv
cat clinical_workflows.json | jq -r ' .[] | .name, .version' | paste - - | sort -u | awk '{print "CLINICAL\t"$0}' >> vidarr_tags.tsv
cat research_workflows.json | jq -r ' .[] | .name, .version' | paste - - | sort -u | awk '{print "RESEARCH\t"$0}' >> vidarr_tags.tsv
