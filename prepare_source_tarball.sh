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

define_default_value WORK_DIR "$(mktemp --directory)/"
define_default_value TAR_FILE "RetroShare.tar.gz"
define_default_value SRC_DIR "$(realpath $(dirname $BASH_SOURCE)/../../)"

ORIG_DIR="$(pwd)"

[ "$(ls "${SRC_DIR}/supportlibs/restbed/" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --init supportlibs/restbed
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --init dependency/asio
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --init dependency/catch
	git -C ${SRC_DIR}"/supportlibs/restbed" submodule update --init dependency/kashmir
}

[ "$(ls "${SRC_DIR}/supportlibs/udp-discovery-cpp" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --init supportlibs/udp-discovery-cpp 
}

[ "$(ls "${SRC_DIR}/supportlibs/rapidjson" | wc -l)" -lt "5" ] &&
{
	git -C ${SRC_DIR} submodule update --init supportlibs/rapidjson 
}

cd "${WORK_DIR}"
rsync -a --delete \
	--exclude='.git' \
	--filter=':- build_scripts/OBS/.gitignore' \
	"${SRC_DIR}/" RetroShare/

## Source_Version File
#RE_VERSION='s/^[[:alpha:]](.*)-g.*$/\1/g'
RE_VERSION='s/^[[:alpha:]]//g'
VERSION="$(git -C ${SRC_DIR} describe)"
DEBVERSION=`echo $VERSION | sed -E "$RE_VERSION" | sed "s/-/./g"`
echo ${VERSION} > RetroShare/Source_Version
cat RetroShare/Source_Version

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
DEB_DESCR_GUI="RetroShare/build_scripts/OBS/network:retroshare/retroshare-gui-unstable/retroshare-gui-unstable.dsc"
DEB_DESCR_CMN="RetroShare/build_scripts/OBS/network:retroshare/retroshare-common-unstable/retroshare-common-unstable.dsc"
sed -i "s/Version: 0.6.9999/Version: ${DEBVERSION}-1/g" ${DEB_DESCR_GUI}
sed -i "s/Version: 0.6.9999/Version: ${DEBVERSION}-1/g" ${DEB_DESCR_CMN}
echo "### Debian GUI Description"
cat ${DEB_DESCR_GUI}
echo "###"

## openSUSE:Specfile
OBS_SPEC_GUI="RetroShare/build_scripts/OBS/network:retroshare/retroshare-gui-unstable/retroshare-gui-unstable.spec"
sed -i "s/Version:       0.6.9999/Version:       ${DEBVERSION}/g" ${OBS_SPEC_GUI}
echo "### openSUSE:Specfile"
cat ${OBS_SPEC_GUI}
echo "###"
echo "Making Archive ..."
tar -zcf ${TAR_FILE} RetroShare/
MD5=`md5sum ${TAR_FILE} | awk '{ print $1 }'`
SIZE=`wc -c ${TAR_FILE} | awk '{ print $1 }'`
echo ""
echo "MD5                              Size     Name"
echo "${MD5} ${SIZE} ${TAR_FILE}"
mv ${TAR_FILE} "${ORIG_DIR}/${TAR_FILE}"
rm -rf "${WORK_DIR}" 
echo "Preparation for git version ${VERSION} and debian ${DEBVERSION} finished."
