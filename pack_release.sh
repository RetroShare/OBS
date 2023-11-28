#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage $0 <release version>"
    echo "Example $0 1.5.9999"
    exit -1
fi

mReleaseVersion=$1

pushd "network:retroshare"


function obs_file_rename()
{
    mv $1 $2
    sed -i "s/$1/$2/g" _service
}

for mPackage in \
    "retroshare-common" \
    "retroshare-friendserver" \
    "retroshare-gui" \
    "retroshare-service" ;
do
    mDestDir="$mPackage-$mReleaseVersion"

    rm -rf "$mDestDir"
    cp -r "$mPackage-unstable/" "$mDestDir/"

    pushd "$mDestDir/"

    sed -i "s|/$mPackage-unstable/|/$mDestDir/|g" _service

    obs_file_rename debian.$mPackage-unstable.install debian.$mPackage.install
    obs_file_rename $mPackage-unstable.dsc $mPackage.dsc
    obs_file_rename $mPackage-unstable.spec $mPackage.spec

    sed -i "s/app: $mPackage-unstable/app: $mPackage-$mReleaseVersion/" appimage.yml
    sed -i "s/-DRS_MINI_VERSION=9999 / /" appimage.yml   # CMake
    sed -i "s/ RS_MINI_VERSION=9999 / /"  appimage.yml   # Qmake

    echo "$mPackage ($mReleaseVersion) stable; urgency=low

    Add $mPackage $mReleaseVersion package

 -- RetroShare Team <contact@retroshare.cc>  $(date -R)" > debian.changelog

    sed -i "s/Source: $mPackage-unstable/Source: $mPackage/" debian.control
    sed -i "s/Package: $mPackage-unstable/Package: $mPackage/" debian.control
    sed -i "s/Depends: retroshare-common-unstable/Depends: retroshare-common/" debian.control

    sed -i "s/-DRS_MINI_VERSION=9999 / /" debian.rules
    sed -i "s/ RS_MINI_VERSION=9999 / /"  debian.rules

    sed -i "s/pkgname=$mPackage-unstable/pkgname=$mPackage/" PKGBUILD
    sed -i "s/pkgver=unstable/pkgver=$mReleaseVersion/" PKGBUILD
    sed -i "s/pkgrel=[0-9]\+/pkgrel=$(date '+%Y%m%d')/" PKGBUILD
    sed -i "s/-DRS_MINI_VERSION=9999 / /" PKGBUILD
    sed -i "s/ RS_MINI_VERSION=9999 / /"  PKGBUILD

    sed -i "s/Source: $mPackage-unstable/Source: $mPackage/" $mPackage.dsc
    sed -i "s/Binary: $mPackage-unstable/Binary: $mPackage/" $mPackage.dsc
    sed -i "s/Version: [0-9]\+.[0-9]\+.9999/Version: $mReleaseVersion/" $mPackage.dsc

    sed -i "s/Name: \+$mPackage-unstable/Name: $mPackage/" $mPackage.spec
    sed -i "s/Version: \+[0-9]\+.[0-9]\+.9999/Version: $mReleaseVersion/" $mPackage.spec
    sed -i "s/Conflicts: \+$mPackage/Conflicts: $mPackage-unstable/" $mPackage.spec
    sed -i "s/-DRS_MINI_VERSION=9999 / /" $mPackage.spec
    sed -i "s/ RS_MINI_VERSION=9999 / /"  $mPackage.spec

    popd
done

popd
