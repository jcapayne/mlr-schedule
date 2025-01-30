#!/bin/sh

for r in *.ics
do
  FILEHASH=$(sha512 -q ${r})
  WEBHASH=$(curl -sS https://rangerpicks.rugby/uploads/2025/${r} | sha512 -q)
  if [ "x${FILEHASH}" != "x${WEBHASH}" ]
  then
    echo "${r} is different"
    curl -H 'Authorization: Bearer 6CEA5DC1F76ACB4CE616' 'https://micro.blog/micropub/media?mp-destination=https://rangerpicks.rugby/' -F "file=@${r}"
    echo ""
    #  echo "Uploaded ${UPLOADFILE} you need to rename it"
    #fi
  fi
done
