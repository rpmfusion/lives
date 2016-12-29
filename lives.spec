# Filtering of private libraries
%global privlibs libOSC
%global privlibs %{privlibs}|libOSC_client
%global privlibs %{privlibs}|libweed
%global privlibs %{privlibs}|libweed-utils
%global privlibs %{privlibs}|libweed-utils_scripting
%global privlibs %{privlibs}|libweed_slice
%global privlibs %{privlibs}|libweed_slice_scripting

%global __provides_exclude ^(%{privlibs})\\.so
%global __requires_exclude ^(%{privlibs})\\.so
#

Name:           lives
Version:        2.8.3
Release:        1%{?dist}
Summary:        Video editor and VJ tool
License:        GPLv3+ and LGPLv3+
URL:            http://lives-video.com
Source0:        http://lives-video.com/releases/LiVES-%{version}.tar.bz2
## Appdata file
Source1:        LiVES.appdata.xml

BuildRequires:  pkgconfig(jack)
BuildRequires:  pkgconfig(sdl)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libunicap)
BuildRequires:  pkgconfig(libdv)
BuildRequires:  pkgconfig(libavc1394)
BuildRequires:  pkgconfig(libraw1394)
BuildRequires:  pkgconfig(libv4lconvert)
BuildRequires:  pkgconfig(libfreenect)
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
%if 0%{?fedora} > 23
BuildRequires:  pkgconfig(libprojectM)
%endif
BuildRequires:  ladspa-devel
BuildRequires:  GLee-devel
BuildRequires:  x264-libs
BuildRequires:  gettext-devel
BuildRequires:  doxygen
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
BuildRequires:  bison
BuildRequires:  gtk3-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  bzip2-devel
BuildRequires:  libappstream-glib
BuildRequires:  gcc-c++
BuildRequires:  perl-generators
BuildRequires:  python2-devel
BuildRequires:  python3-devel

# Packages for re-configuration
BuildRequires:  autoconf, automake, libtool

Requires: mplayer
Requires: mpv
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
%if 0%{?fedora} > 23
Requires: projectM-libvisual
Requires: projectM-pulseaudio
Requires: projectM-jack
%endif
Requires: hicolor-icon-theme

%description
LiVES began in 2002 as the Linux Video Editing System.
Since it now runs on more operating systems: LiVES is a Video Editing System.
It's video editor, VJ tool and video programming environment,
designed to be simple to use, yet powerful.
It is small in size, yet it has many advanced features.

%prep
%setup -q

##Remove spurious executable permissions
for i in `find . -type f \( -name "*.c" -o -name "*.h" -o -name "*.txt" \)`; do
chmod a-x $i
done

# Fix to compile with GCC-6.1.1
%if 0%{?fedora} > 23
sed -e 's|toonz.cpp||g' -i lives-plugins/weed-plugins/Makefile.am
%endif

%build
%if 0%{?fedora} > 23
autoreconf -ivf
%endif
%configure --disable-silent-rules --enable-shared --enable-static \
 --enable-largefile --enable-threads --disable-rpath --enable-profiling \
 --enable-doxygen --disable-libvisual \
%if 0%{?fedora} > 23
 --enable-projectM
%else
 --disable-projectM
%endif
 
%make_build

%install
%make_install
%find_lang %{name}

find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

##We want that these libraries are private
mv %{buildroot}%{_libdir}/libOSC* %{buildroot}%{_libdir}/%{name}
mv %{buildroot}%{_libdir}/libweed* %{buildroot}%{_libdir}/%{name}
#
##Weed's devel files removed
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -rf %{buildroot}%{_includedir}/weed

##Remove bad documentation files location
rm -rf %{buildroot}%{_docdir}/lives-%{version}

##Remove rpaths
chrpath -d %{buildroot}%{_bindir}/lives-exe

# Fix Python interpreter
find %{buildroot} -name 'lives*encoder' -o -name 'multi_encoder' | xargs sed -i '1s|^#!/usr/bin/env python|#!%{__python2}|'
find %{buildroot} -name 'lives*encoder3' -o -name 'multi_encoder3' | xargs sed -i '1s|^#!/usr/bin/env python|#!%{__python3}|'

##Set Exec key
desktop-file-edit \
 --set-key=Exec \
 --set-value="env LD_LIBRARY_PATH=%{_libdir}/%{name} \
 FREI0R_PATH=%{_libdir}/frei0r-1 LADSPA_PATH=%{_libdir}/ladspa lives-exe" \
%{buildroot}%{_datadir}/applications/LiVES.desktop

# Register as an application to be visible in the software center
install -Dp -m 644 %{SOURCE1} %{buildroot}%{_datadir}/appdata/LiVES.appdata.xml

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

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
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/appdata/LiVES.appdata.xml

%changelog
* Thu Dec 29 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.3-1
- Update to 2.8.3

* Mon Nov 28 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.2-1
- Update to 2.8.2

* Wed Oct 26 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.1-3
- Fix python interpreter of 'lives_*_encoder*' scripts (bz#4304)

* Tue Oct 25 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.1-2
- Fix python interpreter of 'multiencoder3' script (bz#4304)

* Mon Oct 24 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.1-1
- Update to 2.8.1

* Mon Oct 24 2016 Paul Howarth <paul@city-fan.org> - 2.8.0-2
- BR: perl-generators for proper dependency generation (https://fedoraproject.org/wiki/Changes/Build_Root_Without_Perl)
- BR: python2-devel for %__python2 macro definition 

* Mon Sep 19 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.0-2
- Drop mencoder as Requires package

* Sat Sep 03 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.8.0-1
- Update to 2.8.0

* Sat Aug 27 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.8-1
- Update to 2.6.8

* Fri Aug 19 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.7-1
- Update to 2.6.7

* Thu Aug 18 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.6-3
- Fix icon installation

* Thu Aug 18 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.6-2
- Add ProjectM support on Fedora >= 24

* Wed Aug 17 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.6-1
- Update to 2.6.6

* Sun Aug 14 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.5-1
- Update to 2.6.5

* Fri Aug 12 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.4-4
- Fix Python interpreter
- Filtering of private libraries

* Thu Aug 11 2016 Antonio Trande <sagitterATfedoraproject.org> - 2.6.4-3
- Update appdata file

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
