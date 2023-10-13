#!/bin/bash

source "$(realpath $(dirname $BASH_SOURCE)/get_source_version.include)"

echo "-DRS_MAJOR_VERSION=${VERSION_MAJOR} -DRS_MINOR_VERSION=${VERSION_MINOR} -DRS_MINI_VERSION=${VERSION_MINI} -DRS_EXTRA_VERSION=\"${VERSION_EXTRA}\""
