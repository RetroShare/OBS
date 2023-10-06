#!/bin/bash

## Define default value for variable, take two arguments, $1 variable name,
## $2 default variable value, if the variable is not already define define it
## with default value.
function define_default_value()
{
	VAR_NAME="${1}"
	DEFAULT_VALUE="${2}"

	[ -z "${!VAR_NAME}" ] && export ${VAR_NAME}="${DEFAULT_VALUE}"
}

ORIG_DIR="$(pwd)"

if ! test -f ${ORIG_DIR}/prepare_source_tarball.sh ; then
	echo This script should be started from the RetroShare/build_scripts/OBS directory. 
	exit 1
fi

TMP_DIR=$(mktemp --directory)

cd $TMP_DIR
git clone --depth 1 git@github.com:csoler/retroshare.git RetroShare

# define_default_value WORK_DIR "$(mktemp --directory)/"
define_default_value TAR_FILE "RetroShare.tar.gz"
define_default_value SRC_DIR ${TMP_DIR}/RetroShare

cd ${TMP_DIR}

[ "$(ls "${SRC_DIR}/supportlibs/restbed/" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/restbed
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --depth 1 --init dependency/asio
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --depth 1 --init dependency/catch
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --depth 1 --init dependency/kashmir
}

[ "$(ls "${SRC_DIR}/supportlibs/udp-discovery-cpp" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/udp-discovery-cpp 
}

# >>>> This forces the script to use the uncommitted OBS code, and should be re-enabled after testing the script.
# [ "$(ls "${SRC_DIR}/build_scripts/OBS" | wc -l)" -lt "5" ] &&
# {
# 	git -C ${SRC_DIR} submodule update --depth 1 --init build_scripts/OBS 
# }
# <<<< This forces the script to use the uncommitted OBS code, and should be re-enabled after testing the script.

[ "$(ls "${SRC_DIR}/supportlibs/rapidjson" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/rapidjson 
}

[ "$(ls "${SRC_DIR}/supportlibs/libsam3" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/libsam3
}

[ "$(ls "${SRC_DIR}/supportlibs/cmark" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/cmark
}

[ "$(ls "${SRC_DIR}/supportlibs/jni.hpp" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init supportlibs/jni.hpp
}

[ "$(ls "${SRC_DIR}/libbitdht" | wc -l)" -lt "1" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init --remote --force libbitdht
}

[ "$(ls "${SRC_DIR}/libretroshare" | wc -l)" -lt "1" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init --remote --force libretroshare
}

[ "$(ls "${SRC_DIR}/openpgpsdk" | wc -l)" -lt "1" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init --remote --force openpgpsdk
}

[ "$(ls "${SRC_DIR}/retroshare-webui" | wc -l)" -lt "1" ] &&
{
	git -C ${SRC_DIR} submodule update --depth 1 --init --remote --force retroshare-webui
}

# Checks if OBS has been updated. In release mode, it is, since we use the scripts from the remote repository. In testing mode it is not, so
# we use the scripts from the local clone from where the scripts are being edited.

if ! test -d ./RetroShare/build_scripts/OBS/network:retroshare ; then
	echo Using local OBS code for creating the package \(testing mode\)
	rsync -a --delete \
		--exclude='**.git*' \
		--exclude='/build_scripts/OBS/network:retroshare/**/.osc**' \
		--exclude='/build_scripts/OBS/network:retroshare/**/binaries**' \
		--exclude='/build_scripts/OBS/network:retroshare/**/*.tar.gz' \
		--exclude='*.a' --exclude='*.so' --exclude='*.o' --exclude='**~' \
		--exclude='*.pro.user' \
		--exclude='*.txt' \
		--exclude='.??*' \
		--exclude='*.log' \
		--exclude='**.kdev4' \
		--exclude='/.kdev4/**' \
		--exclude='CMakeLists.txt.user' \
		--include='/supportlibs/libsam3/Makefile' \
		--exclude='Makefile**' \
		"${ORIG_DIR}/" RetroShare/build_scripts/OBS/
else
	echo Using default committed OBS code for creating the package \(release mode\)
fi

## Source_Version File
#RE_VERSION='s/^[[:alpha:]](.*)-g.*$/\1/g'
RE_VERSION='s/^[[:alpha:]]//g'
VERSION="$(git -C ${SRC_DIR} describe)"
DEBVERSION=`echo $VERSION | sed -E "$RE_VERSION" | sed "s/-/./g"`
echo ${VERSION} > RetroShare/Source_Version
cat RetroShare/Source_Version

echo "Making Archive ..."
tar -zcf ${TAR_FILE} RetroShare/
SIZE=`wc -c ${TAR_FILE} | awk '{ print $1 }'`
MD5=`md5sum ${TAR_FILE} | awk '{ print $1 }'`
echo ""
echo "MD5                              Size     Name"
echo "${MD5} ${SIZE} ${TAR_FILE}"
mv ${TAR_FILE} "${ORIG_DIR}/${TAR_FILE}"

## Update Debian ChangeLog
DEB_CHGLOG_GUI="RetroShare/build_scripts/OBS/network:retroshare/retroshare-gui-unstable/debian.changelog"
DEB_CHGLOG_CMN="RetroShare/build_scripts/OBS/network:retroshare/retroshare-common-unstable/debian.changelog"
>${DEB_CHGLOG_GUI}
function logentry() {
	local version=$1
	local describe=`git -C ${SRC_DIR} describe ${version} | sed -E "$RE_VERSION"`
	echo "retroshare-gui-unstable ($describe) unstable; urgency=low"
	echo
	git -C ${SRC_DIR} show $version --quiet --oneline --format="  * %s:%b"
	echo
	git -C ${SRC_DIR} show $version --quiet --oneline --format=" -- %an <%ae>  %aD"
	echo
}
git -C ${SRC_DIR} log -10 --pretty=format:%H | (
	while read version; do
		logentry $version >> ${DEB_CHGLOG_GUI}
	done
)
sed "s/retroshare-gui-unstable/retroshare-common-unstable/g" ${DEB_CHGLOG_GUI} > ${DEB_CHGLOG_CMN}
echo "### Debian GUI Changelog"
cat ${DEB_CHGLOG_GUI}
echo "###"

## Debian Description

function updatedsc() {		# $1 dsc file to update, $2 md5, $3 size, $4 deb version
	echo Updating file \"$1\" with md5=$2 and size=$3
	sed -i "s/DEBTRANSFORM-TAR/$2\ $3/g" $1 
	sed -i "s/Version: 0.6.9999/Version: $4-1/g" $1
}

DEB_DESCR_GUI=${SRC_DIR}/"build_scripts/OBS/network:retroshare/retroshare-gui-unstable/retroshare-gui-unstable.dsc"
DEB_DESCR_CMN=${SRC_DIR}/"build_scripts/OBS/network:retroshare/retroshare-common-unstable/retroshare-common-unstable.dsc"

updatedsc ${DEB_DESCR_GUI} $MD5 $SIZE $DEBVERSION
updatedsc ${DEB_DESCR_CMN} $MD5 $SIZE $DEBVERSION

echo "### Copying Debian GUI Description"
cp ${DEB_DESCR_GUI} ${ORIG_DIR}/retroshare-gui-unstable.dsc
cp ${DEB_DESCR_CMN} ${ORIG_DIR}/retroshare-common-unstable.dsc
echo "###"

## openSUSE:Specfile

function updatespec() {    # $1 spec file to update, $2 deb version
	sed -i "s/Version:       0.6.9999/Version:       $2/g" $1
}
OBS_SPEC_GUI=${SRC_DIR}/"build_scripts/OBS/network:retroshare/retroshare-gui-unstable/retroshare-gui-unstable.spec"

updatespec ${OBS_SPEC_GUI} ${DEBVERSION}

echo "### Copying GUI spec file"
cp ${OBS_SPEC_GUI} ${ORIG_DIR}/retroshare-gui-unstable.spec
echo "###"
echo [DEBUG] now entering sleep mode so you can examine the directories. Press [ENTER] to continue
read
rm -rf "${TMP_DIR}" 
echo "Preparation for git version ${VERSION} and debian ${DEBVERSION} finished."

[ "$SIZE" -ge "50000000" ] &&
{
	echo "${TAR_FILE} is $SIZE bigger the 50MB some error must have happened!"
	exit -1
}
