#!/bin/bash

# Script to prepare RetroShare Android package building toolchain
#
# Copyright (C) 2019-2023  Gioacchino Mazzurco <gio@retroshare.cc>
# Copyright (C) 2020-2023  Asociación Civil Altermundi <info@altermundi.net>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>
#
# SPDX-FileCopyrightText: Retroshare Team <contact@retroshare.cc>
# SPDX-License-Identifier: AGPL-3.0-only

## Define default value for variable, take two arguments, $1 variable name,
## $2 default variable value, if the variable is not already define define it
## with default value.
function define_default_value()
{
	VAR_NAME="${1}"
	DEFAULT_VALUE="${2}"

	[ -z "${!VAR_NAME}" ] && export ${VAR_NAME}="${DEFAULT_VALUE}"
}

define_default_value WORK_DIR "$(mktemp --directory)/"
define_default_value CLEANUP_WORKDIR true
define_default_value TAR_FILE "RetroShare.tar.gz"
define_default_value SRC_DIR "$(realpath $(dirname $BASH_SOURCE)/../../)"
SRC_DIR="$(realpath "$SRC_DIR")" # Enforce absolute path if passed

ORIG_DIR="$(pwd)"

function git_check_submodule()
{
	local pSubmodulePath="$1" ; shift
	local pRepoPath="${1-$SRC_DIR}" ; shift

	[ "$(ls "${pRepoPath}/${pSubmodulePath}" | wc -l)" -lt "2" ] &&
	{
		# --force removed because can interfere with local modifications
		# --remote removed because doesn't honor the version indicated in the
		#	main repository enforcing checking out last version of the submodule
		#	potentially breaking everything
		git -C "${pRepoPath}" submodule update \
			--depth 1 --init \
			"$pSubmodulePath"
	}
}

# if SRC_DIR does not exists chcekout clean RetroShare source
if [ ! -d "$SRC_DIR" ]; then
	# Full clone so we have the tags too
	git clone git@github.com:RetroShare/RetroShare.git "$SRC_DIR"
	git_check_submodule build_scripts/OBS || exit -2
fi

git_check_submodule supportlibs/restbed
git_check_submodule dependency/asio "${SRC_DIR}/supportlibs/restbed"
git_check_submodule dependency/catch "${SRC_DIR}/supportlibs/restbed"
git_check_submodule dependency/kashmir "${SRC_DIR}/supportlibs/restbed"

git_check_submodule supportlibs/udp-discovery-cpp
git_check_submodule supportlibs/rapidjson
git_check_submodule supportlibs/libsam3
git_check_submodule supportlibs/cmark
git_check_submodule supportlibs/jni.hpp

git_check_submodule libbitdht
git_check_submodule libretroshare
git_check_submodule openpgpsdk
git_check_submodule retroshare-webui

pushd "${WORK_DIR}"
rsync -a --delete \
	--exclude='**.git*' \
	--exclude='/build_scripts/OBS/network:retroshare/**/.osc**' \
	--exclude='/build_scripts/OBS/network:retroshare/**/binaries**' \
	--exclude='/build_scripts/OBS/network:retroshare/**/*.tar.gz' \
	--exclude='*.a' --exclude='*.so' --exclude='*.o' --exclude='**~' \
	--exclude='*.pro.user' \
	--exclude='.gradle/' \
	--exclude='**.kdev4' \
	--exclude='/.kdev4/**' \
	--exclude='CMakeLists.txt.user' \
	--include='/supportlibs/libsam3/Makefile' \
	--exclude='Makefile**' \
	"${SRC_DIR}/" RetroShare/

## Generate Source_Version file that will be used at build time
#RE_VERSION='s/^[[:alpha:]](.*)-g.*$/\1/g'
RE_VERSION='s/^[[:alpha:]]//g'
VERSION="$(git -C ${SRC_DIR} describe --tags)"
echo ${VERSION} > RetroShare/Source_Version

## Put Version details in distribution packages recipes

function set_deb_version()
{
	local mPackageName="$1"

	local DEBVERSION="$(echo $VERSION | sed -E "$RE_VERSION" | sed "s/-/./g")"

	sed -i "s/Version: 0.6.9999/Version: ${DEBVERSION}-1/g" \
		"RetroShare/build_scripts/OBS/network:retroshare/$mPackageName/$mPackageName.dsc"
}

function deb_logentry()
{
	local version="$1"
	local packageName="$2"

	local describe="$(git -C ${SRC_DIR} describe ${version} | sed -E "$RE_VERSION")"

	echo "$packageName ($describe) unstable; urgency=low"
	echo
	git -C ${SRC_DIR} show $version --quiet --oneline --format="  * %s:%b"
	echo
	git -C ${SRC_DIR} show $version --quiet --oneline --format=" -- %an <%ae>  %aD"
	echo
}

function set_deb_changelog()
{
	local packageName="$1"

	local mChangeLogFile="RetroShare/build_scripts/OBS/network:retroshare/$packageName/debian.changelog"

	rm -f "$mChangeLogFile"
	git -C ${SRC_DIR} log -10 --pretty=format:%H | (
		while read version; do
			deb_logentry "$version" "$packageName" >> "$mChangeLogFile"
		done
	)
}

function set_rpm_version()
{
	local mPackageName="$1"

	local mSpecFile="RetroShare/build_scripts/OBS/network:retroshare/$mPackageName/$mPackageName.spec"
	local mPackageVersion="$(echo $VERSION | sed -E "$RE_VERSION" | sed "s/-/./g")"

	sed -i "s/Version:       0.6.9999/Version:       ${mPackageVersion}/g" "${mSpecFile}"
}

for mPackage in \
retroshare-common-unstable retroshare-friendserver-unstable \
retroshare-gui-unstable retroshare-service-unstable ; do
	set_deb_version "$mPackage"
	set_deb_changelog "$mPackage"
	set_rpm_version "$mPackage"
done


echo "Making Archive ..."
tar -zcf ${TAR_FILE} RetroShare/
SIZE="$(wc -c ${TAR_FILE} | awk '{ print $1 }')"
MD5="$(md5sum ${TAR_FILE} | awk '{ print $1 }')"
echo ""
echo "MD5                              Size     Name"
echo "${MD5} ${SIZE} ${TAR_FILE}"
mv ${TAR_FILE} "${ORIG_DIR}/${TAR_FILE}"

$CLEANUP_WORKDIR && rm -rf "${WORK_DIR}"

echo "Preparation for git version ${VERSION} and debian ${DEBVERSION} finished."

[ "$SIZE" -ge "50000000" ] &&
{
	echo "${TAR_FILE} is $SIZE bigger the 50MB some error must have happened!"
	exit -1
}
