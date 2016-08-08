Name:           lives
Version:        2.6.4
Release:        2%{?dist}
Summary:        Video editor and VJ tool
License:        GPLv3+ and LGPLv3+
URL:            http://lives-video.com
Source0:        http://lives-video.com/releases/LiVES-%{version}.tar.bz2
## Appdata file downloaded from http://sourceforge.net/p/lives/code/HEAD/tree/trunk/LiVES.appdata.xml
Source1:        LiVES.appdata.xml

BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(sdl)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libunicap)
BuildRequires:  pkgconfig(libdv)
BuildRequires:  pkgconfig(libavc1394)
BuildRequires:  pkgconfig(libraw1394)
BuildRequires:  pkgconfig(libv4lconvert)
BuildRequires:  pkgconfig(frei0r)
BuildRequires:  pkgconfig(liboil-0.3)
BuildRequires:  pkgconfig(theora)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(schroedinger-1.0)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(opencv)
BuildRequires:  pkgconfig(fftw3)
##No plugins available
#BuildRequires:  pkgconfig(libvisual-0.4)
BuildRequires:  pkgconfig(libmatroska)
BuildRequires:  pkgconfig(mjpegtools)
##libprojectM-2.0.1 not supported
#BuildRequires:  pkgconfig(libprojectM)
BuildRequires:  ladspa-devel
BuildRequires:  GLee-devel
BuildRequires:  x264-libs
BuildRequires:  gettext-devel
BuildRequires:  doxygen
BuildRequires:  chrpath, desktop-file-utils
BuildRequires:  bison
BuildRequires:  gtk3-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  bzip2-devel
BuildRequires:  libappstream-glib

# Packages for re-configuration
#BuildRequires:  autoconf, automake, libtool

Requires: mplayer
Requires: mencoder
Requires: sox
Requires: ImageMagick
Requires: ogmtools
Requires: oggvideotools
Requires: perl
Requires: theora-tools
Requires: youtube-dl
Requires: dvgrab
Requires: icedax
Requires: frei0r-plugins
Requires: mkvtoolnix
Requires: vorbis-tools
Requires: dvgrab
#Requires: projectM-libvisual
#Requires: projectM-pulseaudio
#Requires: projectM-jack
Requires: python2

%description
LiVES began in 2002 as the Linux Video Editing System.
Since it now runs on more operating systems: LiVES is a Video Editing System.
It's video editor, VJ tool and video programming environment,
designed to be simple to use, yet powerful.
It is small in size, yet it has many advanced features.

%prep
%setup -q

# Fix to compile with GCC-6.1.1
%if 0%{?fedora} > 23
sed -e 's|toonz.cpp||g' -i lives-plugins/weed-plugins/Makefile.am
%endif

##Remove spurious executable permissions
for i in `find . -type f \( -name "*.c" -o -name "*.h" -o -name "*.txt" \)`; do
chmod a-x $i
done

%build
%configure --disable-silent-rules --enable-shared --enable-static \
 --enable-largefile --enable-threads --disable-rpath --enable-profiling \
 --enable-doxygen --disable-projectM --disable-libvisual
 
%make_build

%install
%make_install
%find_lang %{name}

find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

##Private libs
mv %{buildroot}%{_libdir}/libOSC* %{buildroot}%{_libdir}/%{name}
mv %{buildroot}%{_libdir}/libweed* %{buildroot}%{_libdir}/%{name}
#
##Weed's devel files removed
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -rf %{buildroot}%{_includedir}/weed

##Remove bad documentation files location
rm -rf %{buildroot}%{_docdir}/lives-%{version}

##Push icon into %{_datadir}/icons/%{name}
mkdir -p %{buildroot}%{_datadir}/icons/%{name}
cp -p %{buildroot}%{_datadir}/app-install/icons/%{name}.png %{buildroot}%{_datadir}/icons/%{name}
rm -rf %{buildroot}%{_datadir}/app-install

##Remove rpaths
chrpath -d %{buildroot}%{_bindir}/lives-exe

##Set Exec key
desktop-file-edit \
 --set-key=Exec \
 --set-value="env LD_LIBRARY_PATH=%{_libdir}/%{name} \
 FREI0R_PATH=%{_libdir}/frei0r-1 LADSPA_PATH=%{_libdir}/ladspa lives-exe" \
%{buildroot}%{_datadir}/applications/LiVES.desktop

# Register as an application to be visible in the software center
install -Dp -m 644 %{SOURCE1} %{buildroot}%{_datadir}/appdata/LiVES.appdata.xml

%post
/bin/touch --no-create %{_datadir}/icons/%{name} &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/%{name} &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/%{name} &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/%{name} &>/dev/null || :

%check
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/*.appdata.xml

%files -f %{name}.lang
%doc README AUTHORS BUGS ChangeLog FEATURES
%doc GETTING.STARTED NEWS OMC/*.txt RFX/*
%license COPYING
%{_bindir}/*%{name}*
%{_bindir}/midistart
%{_bindir}/midistop
%{_bindir}/sendOSC
%{_bindir}/smogrify
%{_libdir}/%{name}/
%{_datadir}/applications/LiVES.desktop
%{_datadir}/%{name}/
%{_datadir}/pixmaps/%{name}.xpm
%{_datadir}/icons/%{name}/
%{_datadir}/appdata/LiVES.appdata.xml

%changelog
* Mon Aug 08 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.4-2
- Drop old patch

* Mon Aug 08 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.4-1
- Update to 2.6.4

* Sat Jul 30 2016 Julian Sikorski <belegdol@fedoraproject.org> - 2.6.3-5
- Rebuilt for ffmpeg-3.1.1

* Sat Jul 09 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.3-4
- Fix again conditional macros

* Sat Jul 09 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.3-3
- Patched for ffmpeg-3.0 on f24 too

* Fri Jul 08 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.3-2
- Fix compatibility with ffmpeg-3.0

* Mon May 09 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.3-1
- Update to 2.6.3

* Mon Mar 28 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.2-1
- Update to 2.6.2

* Sun Mar 27 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.1-1
- Update to 2.6.1

* Mon Feb 01 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.0-1
- Update to 2.6.0

* Sun Jan 24 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.4.8-1
- Update to 2.4.8

* Wed Jan 20 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.4.7-2
- Added patch from upstream commit 2363

* Mon Jan 18 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.4.7-1
- Update to 2.4.7

* Wed Jan 13 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-7
- Included new documentation

* Mon Dec 28 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-6
- Update from revision 2353
- libvisual support disabled

* Mon Dec 28 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-5
- Patched to fix Tools->Preference menu crash

* Wed Dec 23 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-4
- libprojectM-2.0.1 not supported

* Mon Dec 21 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-3
- List BRequires and Requires packages completed
- Weed's devel files removed

* Mon Dec 21 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-2
- License fixed
- frei0r support enabled

* Sat Dec 19 2015 Antonio Trande <sagitterATfedoraproject.org> - 2.4.6-1
- First package
