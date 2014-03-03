#!/bin/bash
#
# Run this script to start a local development server.
# First you must fill you github application credentials below.
#

export GITHUB_CLIENT_ID=$1
export GITHUB_CLIENT_SECRET=$2
export OO_INDEX_GITHUB_USERNAME=openshift
export OO_INDEX_GITHUB_REPONAME=oo-index
export OO_INDEX_QUICKSTART_JSON=quickstart.json

if [ -z "$GITHUB_CLIENT_ID" -o -z "$GITHUB_CLIENT_SECRET" ]; then
	echo "Fill in your github credentials and try again."
	exit 1
fi

set -e

[ -d virtenv ] || virtualenv virtenv
. virtenv/bin/activate
egrep -o '[a-zA-Z0-9-]+==[0-9.]+' setup.py | xargs pip install

python wsgi/myflaskapp.py
