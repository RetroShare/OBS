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

function pause() {
	echo press [ENTER] to continue
	read
}

TMP_DIR=$(mktemp --directory)
OBS_DIR=$(mktemp --directory)

cd $TMP_DIR
git clone git@github.com:retroshare/retroshare.git retroshare-0.6.7		# full depth because we want the last tag

# define_default_value WORK_DIR "$(mktemp --directory)/"
define_default_value SRC_DIR ${TMP_DIR}/retroshare-0.6.7

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

echo

if true ; then
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
		"${ORIG_DIR}/" ${OBS_DIR}/
else
	echo Using default committed OBS code for creating the package \(release mode\)
	pushd ${OBS_DIR}
	git clone git@github.com/retroshare/OBS.git 
	popd
fi

RE_VERSION='s/^[[:alpha:]]//g'
VERSION=`git -C ${SRC_DIR} describe`
DEBVERSION=`echo $VERSION | sed -e "s/-/./2g" | cut -c2-`
RPMVERSION=`echo $VERSION | sed -e "s/-/./g" | cut -c2-`
SRCVERSION=`echo $DEBVERSION | cut -d- -f1`

echo VERSION: ${VERSION}
echo DEB VERSION: ${DEBVERSION}

echo SRC_DIR: ${SRC_DIR}

echo ${VERSION} > ${SRC_DIR}/Source_Version
cat ${SRC_DIR}/Source_Version

## Update Debian ChangeLog

DEB_CHGLOG_GUI=${OBS_DIR}"/network:retroshare/retroshare-gui-unstable/debian.changelog"
DEB_CHGLOG_CMN=${OBS_DIR}"/network:retroshare/retroshare-common-unstable/debian.changelog"

define_default_value TAR_FILE retroshare_${DEBVERSION}.tar.gz
define_default_value DSC_FILE retroshare_${DEBVERSION}.dsc
define_default_value CHG_FILE retroshare_${DEBVERSION}.changes

## Create .tar.gz archive.

echo "Making Archive ..."
find ${TMP_DIR} -name ".git*" -exec rm -rf \{\} \;

cp -r ${ORIG_DIR}/debian.template ${SRC_DIR}/debian	# default files. Some of them are modified afterwards
cat ${ORIG_DIR}/debian.template/changelog | sed -e s/XXXXXX/retroshare/g | sed -e s/YYYYYY/${DEBVERSION}/g > ${SRC_DIR}/debian/changelog

cd ${SRC_DIR}
debuild -S -us -uc -i -d

cp ../retroshare_${DEBVERSION}.dsc              ${ORIG_DIR}/
cp ../retroshare_${DEBVERSION}.tar.gz           ${ORIG_DIR}/
cp ../retroshare_${DEBVERSION}_source.build     ${ORIG_DIR}/
cp ../retroshare_${DEBVERSION}_source.buildinfo ${ORIG_DIR}/
cp ../retroshare_${DEBVERSION}_source.changes   ${ORIG_DIR}/

## openSUSE:Specfile

EXTRA_VERSION=`echo ${DEBVERSION} | cut -d- -f2`
OBS_SPEC_GUI=${ORIG_DIR}"/retroshare.spec"
cat ${ORIG_DIR}/rpm.template/retroshare.spec |sed -e s/ZZZZZZ/${DEBVERSION}/g  | sed -e s/XXXXXX/${RPMVERSION}/g | sed -e s/YYYYYY/${EXTRA_VERSION}/g > ${OBS_SPEC_GUI}

## AppImage

cat ${ORIG_DIR}/appimage.template/appimage.yml | sed -e s/XXXXXX/${DEBVERSION}/g | sed -e s/YYYYYY/${SRCVERSION}/g > ${ORIG_DIR}/appimage.yml

## Now cleanup

rm -rf "${TMP_DIR}" 
rm -rf "${OBS_DIR}" 

echo "Preparation for git version ${VERSION} and debian ${DEBVERSION} finished."

# [ "$SIZE" -ge "50000000" ] &&
# {
# 	echo "${TAR_FILE} is $SIZE bigger the 50MB some error must have happened!"
# 	exit -1
# }
