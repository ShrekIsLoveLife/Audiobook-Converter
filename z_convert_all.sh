#!/usr/bin/env bash

for f in *.{aax,m4b}; do
  echo "$f"
  ./aaxconvert.py "$f"
done
