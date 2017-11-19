#!/usr/bin/env bash

for f in *.aax; do
  echo "$f"
  ./aaxconvert.py "$f"
done
