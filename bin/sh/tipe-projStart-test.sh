#!/bin/sh

# File: tipe-projStart-test.sh

# This is a commandline testing script for TIPE

cd ~/Publishing/testArea/tipe_dev
tipe system_debug --off
tipe project_remove -i xxxxx
rm -r .*
rm -r *
tipe system_debug --on
tipe project_create -i xxxxx -t bookTex -n 'A simple test project' -d ~/Publishing/testArea/tipe_dev/xxxxx
cd ~/Publishing/testArea/tipe_dev/xxxxx
tipe component_type_add -t usfmTex
tipe component_type_add -t vmapper
tipe component_type_add -t vMapper
tipe component_type_remove -t vMapper
tipe component_add -c mat mrk luk jhn rev
tipe component_remove -c rev
tipe
