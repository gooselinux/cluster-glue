%global gname haclient
%global uname hacluster
%global nogroup nobody

# When downloading directly from Mercurial, it will automatically add this prefix
# Invoking 'hg archive' wont but you can add one with: hg archive -t tgz -p "Reusable-Cluster-Components-" -r $upstreamversion $upstreamversion.tar.gz
%global specversion 2
%global upstreamprefix Reusable-Cluster-Components-
%global upstreamversion 1448deafdf79

# Keep around for when/if required
#global alphatag %{upstreamversion}.hg

Name:		cluster-glue
Summary:	Reusable cluster components
Version:	1.0.5
Release:	%{?alphatag:0.}%{specversion}%{?alphatag:.%{alphatag}}%{?dist}
License:	GPLv2+ and LGPLv2+
Url:		http://linux-ha.org/wiki/Cluster_Glue
Group:		System Environment/Base
Source0:	http://hg.linux-ha.org/glue/archive/%{upstreamversion}.tar.bz2
Source1:	lrmadmin.8
Requires:	perl-TimeDate
Requires:       cluster-glue-libs = %{version}-%{release}

ExclusiveArch: i686 x86_64

# Directives to allow upgrade from combined heartbeat packages in Fedora11
Provides:	heartbeat-stonith = 3.0.0-1
Provides:	heartbeat-pils = 3.0.0-1
Obsoletes:	heartbeat-stonith < 3.0.0-1
Obsoletes:	heartbeat-pils < 3.0.0-1

## Setup/build bits

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Build dependencies
BuildRequires: automake autoconf libtool pkgconfig libtool-ltdl-devel
BuildRequires: bzip2-devel glib2-devel python-devel libxml2-devel

%if 0%{?fedora} < 12 && 0%{?rhel} < 6
BuildRequires: e2fsprogs-devel
%else
BuildRequires: libuuid-devel
%endif

# For documentation
BuildRequires: libxslt docbook-style-xsl

# For additional Stonith plugins
#BuildRequires: net-snmp-devel OpenIPMI-devel openhpi-devel libcurl-devel

%prep
%setup -q -n %{upstreamprefix}%{upstreamversion}

./autogen.sh

%{configure}	CFLAGS="${CFLAGS} $(echo '%{optflags}')" \
		--enable-fatal-warnings=no   \
		--localstatedir=%{_var}      \
		--with-daemon-group=%{gname} \
		--with-daemon-user=%{uname}

%build
make %{_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# tree fix up
cp $RPM_SOURCE_DIR/lrmadmin.8 %{buildroot}/%{_mandir}/man8/

# Dont package static libs
find %{buildroot} -name '*.a' -exec rm {} \;
find %{buildroot} -name '*.la' -exec rm {} \;

# Don't package pieces we wont support
rm -rf %{buildroot}/%{_libdir}/stonith
rm -f  %{buildroot}/%{_libdir}/heartbeat/ha_logd
rm -f  %{buildroot}/%{_sbindir}/ha_logger
rm -f  %{buildroot}/%{_sbindir}/hb_report
rm -f  %{buildroot}/%{_sbindir}/meatclient
rm -f  %{buildroot}/%{_sbindir}/stonith
rm -f  %{buildroot}/%{_sbindir}/sbd
rm -f  %{buildroot}/%{_datadir}/cluster-glue/ha_cf_support.sh
rm -f  %{buildroot}/%{_datadir}/cluster-glue/openais_conf_support.sh
rm -f  %{buildroot}/%{_datadir}/cluster-glue/utillib.sh
rm -f  %{buildroot}/%{_datadir}/cluster-glue/combine-logs.pl
rm -f  %{buildroot}/%{_datadir}/cluster-glue/ha_log.sh
rm -rf %{buildroot}/%{_datadir}/doc/cluster-glue/stonith
rm -rf %{buildroot}/%{_mandir}/man1/
rm -rf %{buildroot}/%{_mandir}/man8/meatclient.8
rm -rf %{buildroot}/%{_mandir}/man8/ha_logd.8
rm -rf %{buildroot}/%{_mandir}/man8/stonith.8
rm -f  %{buildroot}/%{_sysconfdir}/init.d/logd

%clean
rm -rf %{buildroot}

# cluster-glue

%description
A collection of common tools that are useful for writing cluster managers 
such as Pacemaker.
Provides a local resource manager that understands the OCF and LSB
standards, and an interface to common STONITH devices.

%files
%defattr(-,root,root)
%{_sbindir}/lrmadmin

%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/RAExec
%dir %{_libdir}/heartbeat/plugins/InterfaceMgr
%{_libdir}/heartbeat/lrmd
%{_libdir}/heartbeat/plugins/RAExec/*.so
%{_libdir}/heartbeat/plugins/InterfaceMgr/*.so


%dir %{_var}/lib/heartbeat
%dir %{_var}/lib/heartbeat/cores
%dir %attr (0700, root, root)		%{_var}/lib/heartbeat/cores/root
%dir %attr (0700, nobody, %{nogroup})	%{_var}/lib/heartbeat/cores/nobody
%dir %attr (0700, %{uname}, %{gname})	%{_var}/lib/heartbeat/cores/%{uname}

%doc %{_mandir}/man8/*
%doc AUTHORS
%doc COPYING

# cluster-glue-libs

%package -n cluster-glue-libs
Summary:	Reusable cluster libraries
Group:		Development/Libraries

%description -n cluster-glue-libs
A collection of libraries that are useful for writing cluster managers 
such as Pacemaker.

%pre
getent group %{gname} >/dev/null || groupadd -r %{gname}
getent passwd %{uname} >/dev/null || \
useradd -r -g %{gname} -d %{_var}/lib/heartbeat/cores/hacluster -s /sbin/nologin \
-c "heartbeat user" %{uname}
exit 0

%post -n cluster-glue-libs -p /sbin/ldconfig

%postun -n cluster-glue-libs -p /sbin/ldconfig

%files -n cluster-glue-libs
%defattr(-,root,root)
%{_libdir}/lib*.so.*
%doc AUTHORS
%doc COPYING.LIB

# cluster-glue-libs-devel

%package -n cluster-glue-libs-devel 
Summary:	Headers and libraries for writing cluster managers
Group:		Development/Libraries
Requires:	cluster-glue-libs = %{version}-%{release}

%description -n cluster-glue-libs-devel
Headers and shared libraries for a useful for writing cluster managers 
such as Pacemaker.

%files -n cluster-glue-libs-devel
%defattr(-,root,root)
%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/test
%dir %{_datadir}/cluster-glue
%{_libdir}/lib*.so
%{_libdir}/heartbeat/ipctest
%{_libdir}/heartbeat/ipctransientclient
%{_libdir}/heartbeat/ipctransientserver
%{_libdir}/heartbeat/transient-test.sh
%{_libdir}/heartbeat/base64_md5_test
%{_libdir}/heartbeat/logtest
%{_includedir}/clplumbing
%{_includedir}/heartbeat
%{_includedir}/stonith
%{_includedir}/pils
%{_datadir}/cluster-glue/lrmtest
%{_libdir}/heartbeat/plugins/test/test.so
%doc AUTHORS
%doc COPYING
%doc COPYING.LIB

%changelog

* Tue May 25 2010 Andrew Beekhof <andrew@beekhof.net> 1.0.5-2
- Fix provides/requires for sub packages to avoid version issues
- Add missing man page
  Resolves: rhbz#594116

* Wed May 12 2010 Andrew Beekhof <andrew@beekhof.net> 1.0.5-1
- Do not build on ppc and ppc64.
  Resolves: rhbz#590981
- Rebase on new upstream version: 1448deafdf79
  Resolves: rhbz#590662
  + High: LRM: lrmd: don't add the cancel option in flush to the running operations (bnc#578644)
  + High: LRM: lrmd: don't flush operations which don't belong to the requesting client (lf#2161)
  + High: LRM: lrmd: on shutdown exit once all operations finished (lf#2340)

* Tue Mar 16 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.2-3
- Remove more unsupported and unneeded functionality
- Resolves: rhbz#553386

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.0.2-2
- Resolves: rhbz#567999
- Do not build cluster-glue on s390 and s390x

* Mon Jan 11 2010 Andrew Beekhof <andrew@beekhof.net> - 1.0.2-1
- Suppress unsupported functionality
- Related: rhbz#553386 - logd initscript FedoraGuidelines compliance
- Update to latest upstream release: aa1f9dee2793
  + Medium: LRM: lrmd: log outcome of monitor once an hour
  + Medium: LRM: lrmd: remove operation history on client unregister and flushing all operations (LF 2161)
  + Medium: LRM: lrmd: restore reset scheduler for children (bnc#551971, lf#2296)
  + Medium: LRM: raexec: close the logd fd too when executing agents (LF 2267)
  + Medium: Tools: hb_report: add -V (version) option and add support for corosync

* Fri Nov 13 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.0-0.11.1.b79635605337.hg
- Fix conditional for RHEL

* Mon Oct 12 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0-0.11.b79635605337.hg
- Fix botched tag

* Mon Oct 12 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0-0.10.b79635605337.hg
- Add install dependancy on perl-TimeDate for hb_report
- Update to upstream version b79635605337
  + Build: fix defines for pacemaker-pygui compatibility.
  + High: Tools: hb_report: log/events combining
  + High: doc: new README for wti_mpc
  + High: hb_report: add man page hb_report.8
  + High: hb_report: extract important events from the logs
  + High: stonith: external/ibmrsa-telnet: add support for later RSA cards
  + High: stonith: wti_mpc: support for MIB versions 1 and 3
  + Logd: Start/stop priorities are not created by configure
  + Med: sbd: Fix definition of size_t.
  + Med: sbd: Nodename comparison should be case insensitive (bnc#534445)
  + Med: wti_nps: add support for internet power switch model (bnc#539912)
  + Medium (LF 2194): LRM: fix return code on RA exec failure
  + Medium: Tools: hb_report: add -v option (debugging)
  + Medium: Tools: hb_report: options -C and -D are obsoleted
  + ha_logd: Fix a compile error/warning.
  + hb_report: report corosync packages too.
  + sbd: Accept -h (bnc#529574)
  + sbd: really fix the sector_size type.

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.0-0.9.d97b9dea436e.hg.1
- rebuilt with new openssl

* Mon Aug 17 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0-0.9.d97b9dea436e.hg
- Include relevant provides: and obsoletes: directives for heartbeat
- Update the tarball from upstream to version d97b9dea436e
  + Include license files
  + Fix error messages in autogen.sh
  + High (bnc#501723): Tools: hb_report: collect archived logs too
  + Medium: clplumbing: check input when creating IPC channels
  + Medium (bnc#510299): stonith: set G_SLICE to always-malloc to avoid bad interaction with the threaded openhpi
  + Med: hb_report: report on more packages and with more state.
  + The -E option to lrmadmin does not take an argument
  + Provide a default value for docdir and ensure it is expanded
  + Low: clplumbing: fix a potential resource leak in cl_random (bnc#525393).
  + Med: hb_report: Include dlm_tool debugging information if available.
  + hb_report: Include more possible error output.
  + Medium: logd: add init script and example configuration file.
  + High: logd: Fix init script. Remove apphbd references.
  + logd: configuration file is optional.
  + logd: print status on finished operations.
  + High: sbd: actually install the binary.
  + Medium: stonith: remove references to heartbeat artifacts.
  + High: hb_report: define HA_NOARCHBIN
  + hb_report: correct syntax error.
  + hb_report: Include details about more packages even.
  + hb_report: report corosync packages too.

* Mon Aug 10 2009 Ville Skyttä <ville.skytta@iki.fi> - 1.0-0.8.75cab275433e.hg
- Use bzipped upstream tarball.

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0-0.7.75cab275433e.hg
- Add a leading zero to the revision when alphatag is used

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0-0.6.75cab275433e.hg
- Incorporate results of Fedora review
  - Use global instead of define
  - Remove unused rpm variable
  - Remove redundant configure options
  - Change version to 1.0.0 pre-release and include Mercurial tag in version

* Mon Jul  27 2009 Andrew Beekhof <andrew@beekhof.net> - 0.9-5
- Use linux-ha.org for Source0
- Remove Requires: $name from -devel as its implied
- Instead of 'daemon', use the user and group from Heartbeat and create it 
  if necessary

* Fri Jul  24 2009 Andrew Beekhof <andrew@beekhof.net> - 0.9-4
- Update the tarball from upstream to version 75cab275433e
- Include an AUTHORS and license file in each package
- Change the library package name to cluster-glue-libs to be more 
  Fedora compliant

* Mon Jul  20 2009 Andrew Beekhof <andrew@beekhof.net> - 0.9-3
- Package the project AUTHORS file
- Have Source0 reference the upstream Mercurial repo

* Tue Jul  14 2009 Andrew Beekhof <andrew@beekhof.net> - 0.9-2
- More cleanups

* Fri Jul  3 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.9-1
- Fedora-ize the spec file

* Fri Jun  5 2009 Andrew Beekhof <andrew@beekhof.net> - 0.9-0
- Initial checkin
