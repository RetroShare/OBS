#!/bin/bash

source "$(realpath $(dirname $BASH_SOURCE)/get_source_version.include)"

echo RS_MAJOR_VERSION=${VERSION_MAJOR} RS_MINOR_VERSION=${VERSION_MINOR} RS_MINI_VERSION=${VERSION_MINI} RS_EXTRA_VERSION=\"${VERSION_EXTRA}\"
