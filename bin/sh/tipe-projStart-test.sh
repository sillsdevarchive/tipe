#!/bin/sh

# File: tipe-projStart-test.sh

# This is a commandline testing script for TIPE

cd ~/Publishing/testArea/tipe_dev
tipe project_remove -i xxxxx
rm -r .*
rm -r *
tipe project_create -i xxxxx -t bookTex -n 'A simple test project' -d ~/Publishing/testArea/tipe_dev/xxxxx
cd ~/Publishing/testArea/tipe_dev/xxxxx
tipe component_type_add -t usfmTex
tipe component_add -c jas -t usfmTex -s ../../Source/59_James.usfm
tipe
