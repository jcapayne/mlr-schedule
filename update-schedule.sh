#!/bin/bash

# if mlr.ics exists, grab the sha512 sum. if not set the sum to 0 to force a change

ICS=$(dirname $0)/mlr.ics


if [ -e ${ICS} ]
then
  OLDHASH=$(/sbin/sha512 -q ${ICS})
  mv ${ICS} ${ICS}.old
else
  OLDHASH=0
fi

$(dirname $0)/schedule-to-ics.py

NEWHASH=$(/sbin/sha512 -q ${ICS})

if [ "x${NEWHASH}" == "x${OLDHASH}" ]
then
  echo "No change"
else
  echo "Schedule changed!"
fi
