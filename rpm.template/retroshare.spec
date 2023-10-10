Name:          retroshare
Version:       XXXXXX
Release:       0
License:       AGPL-3.0-or-later
Summary:       Secure distributed chat, mail, forums, file sharing etc
Group:         Productivity/Networking/Other
Url:           https://retroshare.cc
Source0:       retroshare_ZZZZZZ.tar.gz
#Patch0:       various.patch
BuildRoot:     %{_tmppath}/%{name}
#Conflicts:     retroshare
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
#qt5-qttools-devel qt5-qttools-static
BuildRequires: qt5-qtmultimedia-devel qt5-qtx11extras-devel libXScrnSaver-devel
%endif

%if 0%{?centos_version} == 700
BuildRequires: devtoolset-9-toolchain devtoolset-9-libstdc++-devel
# devtoolset-X-gdb require to specify either python-libs or python27-python-libs
BuildRequires: python27-python-libs
%endif

%if 0%{?fedora_version}
BuildRequires: gcc-c++
BuildRequires: fdupes xapian-core-devel libXScrnSaver-devel
BuildRequires: qt5-qtbase-devel qt5-qttools-devel qt5-qttools-static
BuildRequires: qt5-qtx11extras-devel qt5-qtmultimedia-devel
%endif

%if %{defined mageia}
BuildRequires: gcc-c++
BuildRequires: libzlib-devel libbzip2-devel
BuildRequires: libqt5core-devel libqt5xml-devel libxapian-devel
BuildRequires: libqt5x11extras-devel libxscrnsaver-devel libqt5multimedia-devel
BuildRequires: libqt5designer-devel
BuildRequires: libqt5gui-devel libqt5printsupport-devel
%endif

%if 0%{?suse_version}
%if %{suse_version} != 1550
BuildRequires: gcc7 gcc7-c++
%endif
BuildRequires: fdupes libbz2-devel 
BuildRequires: libqt5-qtbase-devel libqt5-qttools-devel
BuildRequires: libxapian-devel update-desktop-files
BuildRequires: libqt5-qtx11extras-devel
BuildRequires: libqt5-qtmultimedia-devel libXScrnSaver-devel
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

%package service
Summary: headless retroshare client, controlled by a web interface
Requires: retroshare-common 
%description service
RetroShare is a Free and Open Source, private and secure decentralized 
communication platform. Contains web interface files and DHT bootstrapping data.
See retroshare-gui package.

Authors:
see https://retroshare.cc/

%package gui
Summary: Graphical user interface for retroshare, based on Qt
Requires: retroshare-common
%description gui
RetroShare is a cross-platform F2F communication platform.
It lets you share securely with your friends, using PGP
to authenticate peers and OpenSSL to encrypt all communication.
RetroShare provides filesharing, chat, messages and channels.

Authors:
see https://retroshare.cc/

%package friendserver
Summary: A friend server for retroshare Tor nodes.
%description friendserver
A friend server for retroshare Tor nodes.

Authors:
see https://retroshare.cc/

%package common
Summary: Web interface and DHT bootstrapping data for retroshare
%description common
RetroShare is a Free and Open Source, private and secure decentralized 
communication platform. Contains web interface files and DHT bootstrapping data.
See retroshare-gui package.

Authors:
see https://retroshare.cc/
--------

%prep
%setup -n retroshare-0.6.7
#%%patch0 -p0

%build

echo centos_version: %{?centos_version} mageia: %{?mageia} \
	mageia_version: %{?mageia_version}

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
BUILD_DEEPSEARCH="CONFIG+=rs_deep_search"
BUILD_JSONAPI="CONFIG+=rs_jsonapi"
BUILD_WEBUI="CONFIG+=rs_webui"
QMAKE="qmake-qt5"

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

%if %{defined suse_version} && 0%{?suse_version} != 1550
BUILD_CC="QMAKE_CC=gcc-7"
BUILD_CXX="QMAKE_CXX=g++-7"
%endif

$QMAKE -r $BUILD_CC $BUILD_CXX QMAKE_STRIP=echo PREFIX="%{_prefix}" \
	BIN_DIR="%{_bindir}" LIB_DIR="%{_libdir}" \
	DATA_DIR="%{_datadir}/retroshare" \
	RS_MAJOR_VERSION=0 RS_MINOR_VERSION=6 RS_MINI_VERSION=7 \
	RS_EXTRA_VERSION="YYYYYY" \
	CONFIG-=debug CONFIG+=release \
	CONFIG+=no_retroshare_plugins \
	CONFIG+=c++14 \
	${BUILD_JSONAPI} ${BUILD_WEBUI} ${BUILD_SQLCIPHER} \
	RetroShare.pro
make -j$(nproc)

%install
rm -rf $RPM_BUILD_ROOT
make INSTALL_ROOT=$RPM_BUILD_ROOT install

%if %{defined centos_version} || %{defined mageia}
%else
%fdupes %{buildroot}/%{_prefix}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

# empty files section so as to *not* build the main package
%files

%files common
%defattr(644, root, root)
%{_datadir}/retroshare
%{_datadir}/retroshare/bdboot.txt
%{_datadir}/retroshare/webui/app.js 
%{_datadir}/retroshare/webui/index.html 
%{_datadir}/retroshare/webui/styles.css 
%{_datadir}/retroshare/webui/webfonts/
%{_datadir}/retroshare/webui/webfonts/fa-solid-900.eot
%{_datadir}/retroshare/webui/webfonts/fa-solid-900.svg
%{_datadir}/retroshare/webui/webfonts/fa-solid-900.ttf
%{_datadir}/retroshare/webui/webfonts/fa-solid-900.woff
%{_datadir}/retroshare/webui/webfonts/fa-solid-900.woff2
%{_datadir}/retroshare/webui/images/retroshare.svg 

%files service
%{_bindir}/retroshare-service

%files friendserver
%{_bindir}/retroshare-friendserver

%files gui
%defattr(-, root, root)
%{_bindir}/retroshare
%{_datadir}/applications/retroshare.desktop 
%{_datadir}/icons/hicolor/128x128/apps/retroshare.png 
%{_datadir}/icons/hicolor/24x24/apps/retroshare.png
%{_datadir}/icons/hicolor/48x48/apps/retroshare.png
%{_datadir}/icons/hicolor/64x64/apps/retroshare.png
%{_datadir}/pixmaps/retroshare.xpm
%{_datadir}/retroshare/qss/retroclassic.qss 
%{_datadir}/retroshare/sounds/alert.wav 
%{_datadir}/retroshare/sounds/chat1.wav 
%{_datadir}/retroshare/sounds/chat2.wav 
%{_datadir}/retroshare/sounds/file.wav 
%{_datadir}/retroshare/sounds/ft_complete.wav 
%{_datadir}/retroshare/sounds/ft_incoming.wav 
%{_datadir}/retroshare/sounds/incomingchat.wav 
%{_datadir}/retroshare/sounds/notify.wav 
%{_datadir}/retroshare/sounds/offline.wav 
%{_datadir}/retroshare/sounds/online1.wav 
%{_datadir}/retroshare/sounds/online2.wav 
%{_datadir}/retroshare/sounds/receive.wav 
%{_datadir}/retroshare/sounds/send1.wav 
%{_datadir}/retroshare/sounds/send2.wav 
%{_datadir}/retroshare/sounds/startup.wav 
%{_datadir}/retroshare/stylesheets/Bubble/history/hincoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/houtgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_CL.png
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-blue/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-green/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-grey/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-orange/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/img/bubble-red/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/history/incoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/info.xml 
%{_datadir}/retroshare/stylesheets/Bubble/history/main.css 
%{_datadir}/retroshare/stylesheets/Bubble/history/ooutgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/outgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/system.htm 
%{_datadir}/retroshare/stylesheets/Bubble/history/variants/color.css 
%{_datadir}/retroshare/stylesheets/Bubble/history/variants/standard.css 
%{_datadir}/retroshare/stylesheets/Bubble/private/hincoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/houtgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-blue/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-green/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-grey/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-orange/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/img/bubble-red/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/private/incoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/info.xml 
%{_datadir}/retroshare/stylesheets/Bubble/private/main.css 
%{_datadir}/retroshare/stylesheets/Bubble/private/ooutgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/outgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/system.htm 
%{_datadir}/retroshare/stylesheets/Bubble/private/variants/color.css 
%{_datadir}/retroshare/stylesheets/Bubble/private/variants/standard.css 
%{_datadir}/retroshare/stylesheets/Bubble/public/hincoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/public/houtgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-blue/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-green/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-grey/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-orange/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/img/bubble-red/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/public/incoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble/public/info.xml 
%{_datadir}/retroshare/stylesheets/Bubble/public/main.css 
%{_datadir}/retroshare/stylesheets/Bubble/public/ooutgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/public/outgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble/public/system.htm
%{_datadir}/retroshare/stylesheets/Bubble/public/variants/color.css 
%{_datadir}/retroshare/stylesheets/Bubble/public/variants/standard.css 
%{_datadir}/retroshare/stylesheets/Bubble/src/img.svg 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-blue/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-green/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-grey/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-orange/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/img/bubble-red/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble/src/make_images.sh 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/hincoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/houtgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-blue/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-green/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_CL.png
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-grey/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-orange/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_BC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_BL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_BR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_CC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_CL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_CR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_TC.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_TL.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_TR.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_tick-left.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_tick-right.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/img/bubble-red/bubble_tick.png 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/incoming.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/info.xml 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/main.css 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/ooutgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/outgoing.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/system.htm 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/variants/color.css 
%{_datadir}/retroshare/stylesheets/Bubble_Compact/private/variants/standard.css 


%changelog
