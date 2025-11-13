#!/bin/bash

mkdir -v data/dev
chown :django data/dev
chmod 775 data/dev
chmod g+s data/dev
