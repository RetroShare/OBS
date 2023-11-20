Name:          retroshare-service-unstable
Version:       0.6.9999
Release:       0
License:       AGPL-3.0-or-later
Summary:       Secure distributed chat, mail, forums, file sharing etc
Group:         Productivity/Networking/Other
Url:           https://retroshare.cc
Source0:       RetroShare.tar.gz
#Patch0:       various.patch
BuildRoot:     %{_tmppath}/%{name}
Conflicts:     retroshare-service
BuildRequires: cmake git openssl-devel

%if %{defined centos_version}
# Neither miniupnpc-devel nor libupnp-devel are available on CentOS
%elif 0%{?fedora_version}
BuildRequires: miniupnpc-devel
%elif %{defined mageia}
BuildRequires: lib64miniupnpc-devel
%else
BuildRequires: libminiupnpc-devel
#BuildRequires: libupnp-devel
%endif

%if %{defined centos_version}
# SQLCipher is not availabe on CentOS
BuildRequires: sqlite-devel
%else
BuildRequires: sqlcipher-devel
%endif

%if 0%{?centos_version} == 700 || 0%{?sle_version} == 120300
# rpm on CentOS 7 and openSUSE Leap 42.3 doesn't support boolean dependencies
BuildRequires: doxygen
%else
# Doxygen 1.8.16 bug https://github.com/doxygen/doxygen/issues/7236 breaks build
BuildRequires: (doxygen < 1.8.16 or doxygen > 1.8.16)
%endif

%if %{defined centos_version}
BuildRequires: qt5-qtbase-devel
%endif

%if 0%{?centos_version} == 700
BuildRequires: devtoolset-9-toolchain devtoolset-9-libstdc++-devel
# devtoolset-X-gdb require to specify either python-libs or python27-python-libs
BuildRequires: python27-python-libs
%endif

%if 0%{?fedora_version}
BuildRequires: gcc-c++
BuildRequires: fdupes xapian-core-devel
BuildRequires: qt5-qtbase-devel qt5-qttools-devel qt5-qttools-static
%endif

%if %{defined mageia}
BuildRequires: gcc-c++
BuildRequires: libzlib-devel libbzip2-devel
BuildRequires: libqt5core-devel libqt5xml-devel libxapian-devel

# On Mageia we need this build dependency to avoid this error at linking time
# g++: error: /usr/lib64/libQt5Gui.so: No such file or directory
BuildRequires: libqt5gui-devel
%endif

%if 0%{?suse_version}
BuildRequires: gcc7 gcc7-c++
BuildRequires: fdupes libbz2-devel
BuildRequires: libqt5-qtbase-devel libqt5-qttools-devel
BuildRequires: libxapian-devel update-desktop-files
%endif

%if 0%{?fedora_version} >= 27 || 0%{?centos_version} >= 800
%undefine _debugsource_packages
%undefine _debuginfo_subpackages
%endif


%description
RetroShare is a cross-platform F2F communication platform.
It lets you share securely with your friends, using PGP
to authenticate peers and OpenSSL to encrypt all communication.
RetroShare provides filesharing, chat, messages and channels.
This package provides RetroShare system service that can be
controlled only via JSON API.

Authors:
see https://retroshare.cc/
--------

%prep
%setup -n RetroShare
#%%patch0 -p0

%build

[ "$(doxygen --version)" == "1.8.16" ] && {
	echo Doxygen 1.8.16 is not supported due to \
		https://github.com/doxygen/doxygen/issues/7236 please report it \
		to your distribution
	exit -1
}

cmake --version
qmake --version || qmake-qt5 --version
gcc --version
ls $(which gcc)*
ls $(which g++)*

BUILD_CC=""
BUILD_CXX=""
QMAKE="qmake-qt5"

# Keep default sam3 beaviour for most distributions
BUILD_SAM3=""
%if %{defined mageia} || %{defined fedora_version}
# libsam3 won't compile in Mageia and Fedora due to some too lax code
# see https://github.com/RetroShare/libretroshare/issues/60
# see https://github.com/i2p/libsam3/issues/20
# see https://github.com/i2p/libsam3/pull/21
# keep disabled until the fixes are accepted upstream
BUILD_SAM3="CONFIG+=no_rs_sam3 CONFIG+=no_rs_sam3_libsam3"
%endif

%if %{defined centos_version}
# Xapian is not availabe on CentOS
BUILD_DEEPSEARCH="CONFIG+=no_rs_deep_search"
# SQLCipher is not availabe on CentOS
BUILD_SQLCIPHER="CONFIG+=no_sqlcipher"
%endif

%if 0%{?centos_version} == 700
source /opt/rh/devtoolset-9/enable
%endif

%if %{defined mageia}
QMAKE="qmake"
%endif

%if 0%{?suse_version}
BUILD_CC="QMAKE_CC=gcc-7"
BUILD_CXX="QMAKE_CXX=g++-7"
%endif

## Qmake
$QMAKE $BUILD_CC $BUILD_CXX QMAKE_STRIP=echo PREFIX="%{_prefix}" \
	BIN_DIR="%{_bindir}" LIB_DIR="%{_libdir}" \
	RS_DATA_DIR="%{_datadir}/retroshare" \
	$(build_scripts/OBS/get_source_version.sh) RS_MINI_VERSION=9999 \
	CONFIG+=release CONFIG-=debug CONFIG+=no_retroshare_friendserver \
	CONFIG+=no_retroshare_gui CONFIG+=no_tests \
	CONFIG+=retroshare_service CONFIG+=rs_jsonapi CONFIG+=no_rs_webui \
	CONFIG+=c++14 \
	${BUILD_SQLCIPHER} ${BUILD_SAM3} \
	RetroShare.pro

## CMake
# mkdir cmake_build_tree
# cd cmake_build_tree
# cmake -DRS_SERVICE_DESKTOP=ON -DRS_FORUM_DEEP_INDEX=ON -DRS_WARN_LESS=ON \
# 	-DRS_WARN_DEPRECATED=OFF -DRS_SPLIT_DEBUG=ON \
# 	$(../build_scripts/OBS/get_source_version_cmake.sh) \
# 	-DRS_MINI_VERSION=9999 \
# 	-DCMAKE_INSTALL_PREFIX=$RPM_BUILD_ROOT/%{_prefix} \
# 	../retroshare-service/CMakeLists.txt -B.

make -j$(nproc) || (make && (echo "Parallel build failed" ; exit -1))

%install
rm -rf $RPM_BUILD_ROOT

## CMake
# cd cmake_build_tree
# make install

## Qmake
make INSTALL_ROOT=$RPM_BUILD_ROOT install

%if %{defined centos_version} || %{defined mageia}
%else
%fdupes %{buildroot}/%{_prefix}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%{_bindir}/retroshare-service
%defattr(644, root, root)
%{_datadir}/retroshare
%{_datadir}/retroshare/bdboot.txt

## CMake only
# %{_prefix}/data/retroshare-service.desktop
# %{_datadir}/icons/hicolor/128x128/apps/retroshare-service.png
# %{_datadir}/icons/hicolor/48x48/apps/retroshare-service.png
# %{_datadir}/icons/hicolor/scalable/retroshare-service.svg

%changelog
