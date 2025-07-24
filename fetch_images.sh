#!/usr/bin/env bash

set -e
set -x

ROOT_DIR=$(pwd)/"images"
DIR_1804="$ROOT_DIR/18.04"
DIR_2404="$ROOT_DIR/24.04"

mkdir -p "$ROOT_DIR"
mkdir -p "$DIR_1804"
mkdir -p "$DIR_2404"

if ! command -v wget &> /dev/null; then
    echo "wget could not be found, please install it."
    exit 1
fi

# wget options (check if exists), don't create .1 files
WGET_OPTIONS="--no-clobber"

# 18.04 bionic
cd "$DIR_1804"
wget $WGET_OPTIONS http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/initrd.gz
wget $WGET_OPTIONS http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/linux

# 24.04 noble
cd "$DIR_2404"
wget $WGET_OPTIONS http://archive.ubuntu.com/ubuntu/dists/noble/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/initrd.gz
wget $WGET_OPTIONS http://archive.ubuntu.com/ubuntu/dists/noble/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64/linux