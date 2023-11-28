Name: retroshare-friendserver
Version: 0.6.7
Release:       0
License:       AGPL-3.0-or-later
Summary:       Secure distributed chat, mail, forums, file sharing etc
Group:         Productivity/Networking/Other
Url:           https://retroshare.cc
Source0:       RetroShare.tar.gz
#Patch0:       various.patch
BuildRoot:     %{_tmppath}/%{name}
Conflicts: retroshare-friendserver-unstable
BuildRequires: cmake git openssl-devel

%if %{defined centos_version}
# Neither miniupnpc-devel nor libupnp-devel are available on CentOS
%else
BuildRequires: libupnp-devel
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
BuildRequires: fdupes
BuildRequires: qt5-qtbase-devel qt5-qttools-devel qt5-qttools-static
%endif

%if %{defined mageia}
BuildRequires: gcc-c++
BuildRequires: libzlib-devel libbzip2-devel
BuildRequires: libqt5core-devel

# On Mageia we need this build dependency to avoid this error at linking time
# g++: error: /usr/lib64/libQt5Gui.so: No such file or directory
BuildRequires: libqt5gui-devel
%endif

%if 0%{?suse_version}
BuildRequires: gcc7 gcc7-c++
BuildRequires: fdupes libbz2-devel 
BuildRequires: libqt5-qtbase-devel libqt5-qttools-devel
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
This package provide only RetroShare friendserver an easier way to bootstrap
your trusted nodes network.

Authors:
see https://retroshare.cc/
--------

%prep
%setup -n RetroShare
#%%patch0 -p0

%build

echo centos_version: %{?centos_version} mageia: %{?mageia} \
	mageia_version: %{?mageia_version} suse_version: %{?suse_version}  \
	fedora_version: %{?fedora_version}

[ "$(doxygen --version)" == "1.8.16" ] && {
	echo Doxygen 1.8.16 is not supported due to \
		https://github.com/doxygen/doxygen/issues/7236 please report it \
		to your distribution
	exit -1
}

nproc
qmake --version || qmake-qt5 --version
ls $(which gcc)*
ls $(which g++)*
gcc --version

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

$QMAKE $BUILD_CC $BUILD_CXX QMAKE_STRIP=echo PREFIX="%{_prefix}" \
	BIN_DIR="%{_bindir}" LIB_DIR="%{_libdir}" \
	RS_DATA_DIR="%{_datadir}/retroshare" \
	$(build_scripts/OBS/get_source_version.sh) \
	CONFIG-=debug CONFIG+=release \
	CONFIG+=no_retroshare_plugins CONFIG+=no_retroshare_gui CONFIG+=no_tests \
	CONFIG+=no_retroshare_service CONFIG+=retroshare_friendserver \
	CONFIG+=c++14 \
	${BUILD_SQLCIPHER} ${BUILD_SAM3} \
	RetroShare.pro
make -j$(nproc) || (make && (echo "Parallel build failed" ; exit -1))

%install
rm -rf $RPM_BUILD_ROOT
make INSTALL_ROOT=$RPM_BUILD_ROOT install

%if %{defined centos_version} || %{defined mageia}
%else
%fdupes %{buildroot}/%{_prefix}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%{_bindir}/retroshare-friendserver
%defattr(644, root, root)
%{_datadir}/retroshare
%{_datadir}/retroshare/bdboot.txt

%changelog
