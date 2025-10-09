#!/bin/bash

# GEUNDUUN_URL=${GEUNDUUN_URL:-""}
ROOT_RUNPOD_API_KEY=${ROOT_RUNPOD_API_KEY:-""}
LOG_DIR=${LOG_DIR:-"/workspace/logs"}

# log
mkdir -p ${LOG_DIR}
LOG_FILE=${LOG_DIR}/$(date +"%Y%m%d_%H%M%S").txt
exec > >(tee -a $LOG_FILE) 2>&1

# run script
"$@"
status=$?

# alarm
curl --silent \
    --header "Content-Type: application/json" \
    --request POST \
    --data '{"text": "job finished"}' \
    "${SLACK_WEBHOOK_URL}"

# report to geunduun
# if [[ ${status} -eq 0 ]]; then
#     completion_payload='{"success": true}'
# else
#     completion_payload=$(printf '{"success": false, "message": "Workload exited with status %s"}' "${status}")
# fi
# curl --silent --show-error --fail \
#     --request POST \
#     --header "Content-Type: application/json" \
#     --data "${completion_payload}" \
#     "${BASE_URL}/pods/${POD_ID}/complete" || echo "Failed to notify pod-launcher" >&2

# delete pod
curl --request DELETE \
    --url https://rest.runpod.io/v1/pods/$RUNPOD_POD_ID \
    --header "Authorization: Bearer $ROOT_RUNPOD_API_KEY"
