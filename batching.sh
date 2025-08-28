#!/bin/bash

# consts
SRC_TRIAL_DIR="/Users/andreyignatov/Downloads"  # TODO: change
DST_RESULT_DIR="/Users/andreyignatov/Downloads"  # TODO: change
SERVICE_PORT=3000  # TODO: m.b. change
SERVICE_HOST="http://127.0.0.1"  # TODO: m.b. change

# BATCH CODE
for filename in $SRC_TRIAL_DIR/*.json; do
	curl -d $filename $SERVICE_HOST:$SERVICE_PORT/nutrition -o $DST_RESULT_DIR/$filename_out.json
done



