#%%global prerelease rc2

Summary:        Email filter with virus scanner and spamassassin support
Name:           amavisd-new
Version:        2.11.1
Release:        4
# LDAP schema is GFDL, some helpers are BSD, core is GPLv2+
License:        GPLv2+ and BSD and GFDL
Group:          Networking/Mail
URL:            http://www.ijs.si/software/amavisd/
Source0:        http://www.ijs.si/software/amavisd/amavisd-new-%{version}%{?prerelease:-%{prerelease}}.tar.bz2
Source2:        amavis-clamd.conf
Source4:        README.fedora
Source5:        README.quarantine
Source8:        amavisd-new-tmpfiles.conf
Source9:        amavisd.service
Source10:       amavisd-snmp.service
Source11:       amavisd-clean-tmp.service
Source12:       amavisd-clean-tmp.timer
Source13:       amavisd-clean-quarantine.service
Source14:       amavisd-clean-quarantine.timer
Source15:       amavis-mc.service
Source16:       amavisd-snmp-zmq.service
Patch0:         amavisd-new-2.10.1-conf.patch
Patch1:         amavisd-init.patch
Patch2:         amavisd-condrestart.patch
# Don't source /etc/sysconfig/network in init script; the network check
# is commented out upstream so there's no apparent reason to source it,
# and it can't be relied upon to exist in recent Fedora builds. Mail
# sent upstream to amavis-users ML 2013-05-10. -adamw
Patch3:         amavisd-new-2.8.0-init_network.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  systemd
Recommends:     clamd
Requires:       tmpwatch
Requires:       binutils
#Requires:       altermime
Requires:       arj
Requires:       bzip2
Requires:       cabextract
Requires:       pax
Requires:       file
Requires:       gzip
Requires:       lzop
Requires:       nomarch
Requires:       p7zip
Requires:       tar
# Uncommon DOS world compressors that might still be used to package viruses
Suggests:       lrzip
# Let's not even suggest this one as it conflicts with mlt (/usr/bin/melt)
#Suggests:       freeze
Suggests:       unzoo
# We probably should parse the fetch_modules() code in amavisd for this list.
# These are just the dependencies that don't get picked up otherwise.
Requires:       perl(Archive::Tar)
Requires:       perl(Archive::Zip) >= 1.14
Requires:       perl(Authen::SASL)
Requires:       perl(Compress::Zlib) >= 1.35
Requires:       perl(Compress::Raw::Zlib) >= 2.017
Requires:       perl(Convert::TNEF)
Requires:       perl(Convert::UUlib)
Requires:       perl(Crypt::OpenSSL::RSA)
Requires:       perl(DBD::SQLite)
Requires:       perl(DBI)
Requires:       perl(Digest::MD5) >= 2.22
Requires:       perl(Digest::SHA)
Requires:       perl(Digest::SHA1)
Requires:       perl(File::LibMagic)
Requires:       perl(IO::Socket::IP)
Requires:       perl(IO::Socket::SSL)
Requires:       perl(IO::Stringy)
Requires:       perl(MIME::Base64)
Requires:       perl(MIME::Body)
Requires:       perl(MIME::Decoder::Base64)
Requires:       perl(MIME::Decoder::Binary)
Requires:       perl(MIME::Decoder::Gzip64)
Requires:       perl(MIME::Decoder::NBit)
Requires:       perl(MIME::Decoder::QuotedPrint)
Requires:       perl(MIME::Decoder::UU)
Requires:       perl(MIME::Head)
Requires:       perl(MIME::Parser)
Requires:       perl(Mail::DKIM) >= 0.31
Requires:       perl(Mail::Field)
Requires:       perl(Mail::Header)
Requires:       perl(Mail::Internet) >= 1.58
Requires:       perl(Mail::SPF)
Requires:       perl(Mail::SpamAssassin)
Requires:       perl(Net::DNS)
Requires:       perl(Net::LDAP)
Requires:       perl(Net::LibIDN)
Requires:       perl(Net::SSLeay)
Requires:       perl(Net::Server) >= 2.0
Requires:       perl(NetAddr::IP)
Requires:       perl(Razor2::Client::Version)
Requires:       perl(Socket6)
Requires:       perl(Time::HiRes) >= 1.49
Requires:       perl(Unix::Syslog)
Requires:       perl(URI)
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%package snmp
Group:          Networking/Mail
Summary:        Exports amavisd SNMP data
Requires:       %{name} = %{version}-%{release}
Requires:       perl(NetSNMP::OID)
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%package zeromq
Group:          Networking/Mail
Summary:        Support for communicating through 0MQ sockets
Requires:       %{name} = %{version}-%{release}
Requires:       perl(ZMQ::Constants)
Requires:       perl(ZMQ::LibZMQ3)
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%package snmp-zeromq
Group:          Networking/Mail
Summary:        Exports amavisd SNMP data and communicates through 0MQ sockets
Requires:       %{name}-zeromq = %{version}-%{release}
Requires:       perl(NetSNMP::OID)
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
amavisd-new is a high-performance and reliable interface between mailer
(MTA) and one or more content checkers: virus scanners, and/or
Mail::SpamAssassin Perl module. It is written in Perl, assuring high
reliability, portability and maintainability. It talks to MTA via (E)SMTP
or LMTP, or by using helper programs. No timing gaps exist in the design
which could cause a mail loss.

%description snmp
This package contains the program amavisd-snmp-subagent, which can be
used as a SNMP AgentX, exporting amavisd statistical counters database
(snmp.db) as well as a child process status database (nanny.db) to a
SNMP daemon supporting the AgentX protocol (RFC 2741), such as NET-SNMP.

It is similar to combined existing utility programs amavisd-agent and
amavisd-nanny, but instead of writing results as text to stdout, it
exports data to a SNMP server running on a host (same or remote), making
them available to SNMP clients (such a Cacti or mrtg) for monitoring or
alerting purposes.

%description zeromq
This package adds support for monitoring and communicating with amavisd
and auxiliary services among themselves through 0MQ sockets (also called ZMQ
or ZeroMQ, or Crossroads I/O or XS). This method offers similar features
as current services amavisd-nanny, amavisd-agent and amavisd-snmp-subagent,
but use message passing paradigm instead of communicating through a shared
Berkeley database. This avoids locking contention, so the gain can be
significant for a busy amavisd setup with lots of child processes.

%description snmp-zeromq
This package contains the program amavisd-snmp-subagent-zmq, which can be
used as a SNMP AgentX, exporting amavisd statistical counters database
(snmp.db) as well as a child process status database (nanny.db) to a
SNMP daemon supporting the AgentX protocol (RFC 2741), such as NET-SNMP.
It supports communicating through 0MQ sockets.

%prep
%setup -q -n %{name}-%{version}%{?prerelease:-%{prerelease}}
%autopatch -p1

install -p -m 644 %{SOURCE4} %{SOURCE5} README_FILES/
sed -e 's,/var/amavis/amavisd.sock\>,%{_localstatedir}/spool/amavisd/amavisd.sock,' -i amavisd-release

%build

%install
rm -rf $RPM_BUILD_ROOT

install -D -p -m 755 amavisd $RPM_BUILD_ROOT%{_sbindir}/amavisd
install -D -p -m 755 amavisd-snmp-subagent $RPM_BUILD_ROOT%{_sbindir}/amavisd-snmp-subagent
install -D -p -m 755 amavisd-snmp-subagent-zmq $RPM_BUILD_ROOT%{_sbindir}/amavisd-snmp-subagent-zmq

mkdir -p $RPM_BUILD_ROOT%{_bindir}
install -p -m 755 amavisd-{agent,nanny,release,signer,status,submit} $RPM_BUILD_ROOT%{_bindir}/
install -p -m 755 amavis-mc $RPM_BUILD_ROOT%{_sbindir}/
install -p -m 755 amavis-services $RPM_BUILD_ROOT%{_bindir}/

install -D -p -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_unitdir}/amavisd.service
install -D -p -m 644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}/amavisd-snmp.service
install -D -p -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_unitdir}/amavisd-clean-tmp.service
install -D -p -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_unitdir}/amavisd-clean-tmp.timer
install -D -p -m 644 %{SOURCE13} $RPM_BUILD_ROOT%{_unitdir}/amavisd-clean-quarantine.service
install -D -p -m 644 %{SOURCE14} $RPM_BUILD_ROOT%{_unitdir}/amavisd-clean-quarantine.timer
install -D -p -m 644 %{SOURCE15} $RPM_BUILD_ROOT%{_unitdir}/amavis-mc.service
install -D -p -m 644 %{SOURCE16} $RPM_BUILD_ROOT%{_unitdir}/amavisd-snmp-zmq.service

mkdir -p -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/clamd.d
install -D -p -m 644 amavisd.conf $RPM_BUILD_ROOT%{_sysconfdir}/amavisd/amavisd.conf
install -D -p -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/clamd.d/amavisd.conf

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/spool/amavisd/{tmp,db,quarantine}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/{clamd.amavisd,amavisd}

install -D -m 644 %{SOURCE8} $RPM_BUILD_ROOT%{_tmpfilesdir}/amavisd-new.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group amavis > /dev/null || %{_sbindir}/groupadd -r amavis
getent passwd amavis > /dev/null || \
  %{_sbindir}/useradd -r -g amavis -d %{_localstatedir}/spool/amavisd -s /sbin/nologin \
  -c "User for amavisd-new" amavis
exit 0

%preun
%systemd_preun amavisd.service
%systemd_preun amavisd-clean-tmp.service
%systemd_preun amavisd-clean-tmp.timer
%systemd_preun amavisd-clean-quarantine.service
%systemd_preun amavisd-clean-quarantine.timer

%preun snmp
%systemd_preun amavisd-snmp.service

%preun zeromq
%systemd_preun amavis-mc.service

%preun snmp-zeromq
%systemd_preun amavisd-snmp-zmq.service

%post
%systemd_post amavisd.service
%systemd_post amavisd-clean-tmp.service
%systemd_post amavisd-clean-tmp.timer
%systemd_post amavisd-clean-quarantine.service
%systemd_post amavisd-clean-quarantine.timer

systemctl enable amavisd-clean-tmp.timer >/dev/null 2>&1 || :
systemctl start amavisd-clean-tmp.timer >/dev/null 2>&1 || :
systemctl enable amavisd-clean-quarantine.timer >/dev/null 2>&1 || :
systemctl start amavisd-clean-quarantine.timer >/dev/null 2>&1 || :

%post snmp
%systemd_post amavisd-snmp.service

%post zeromq
%systemd_post amavis-mc.service

%post snmp-zeromq
%systemd_post amavisd-snmp-zmq.service

%postun
%systemd_postun_with_restart amavisd.service
%systemd_postun_with_restart amavisd-clean-tmp.service
%systemd_postun_with_restart amavisd-clean-tmp.timer
%systemd_postun_with_restart amavisd-clean-quarantine.service
%systemd_postun_with_restart amavisd-clean-quarantine.timer

%postun snmp
%systemd_postun_with_restart amavisd-snmp.service

%postun zeromq
%systemd_postun_with_restart amavis-mc.service

%postun snmp-zeromq
%systemd_postun_with_restart amavisd-snmp-zmq.service

%files
%doc AAAREADME.first LDAP.schema LDAP.ldif RELEASE_NOTES TODO INSTALL
%doc README_FILES test-messages amavisd.conf-* amavisd-custom.conf
%doc LICENSE
%dir %{_sysconfdir}/amavisd/
%{_unitdir}/amavisd.service
%{_unitdir}/amavisd-clean-tmp.service
%{_unitdir}/amavisd-clean-tmp.timer
%{_unitdir}/amavisd-clean-quarantine.service
%{_unitdir}/amavisd-clean-quarantine.timer
%dir %{_sysconfdir}/clamd.d
%config(noreplace) %{_sysconfdir}/amavisd/amavisd.conf
%config(noreplace) %{_sysconfdir}/clamd.d/amavisd.conf
%{_sbindir}/amavisd
%{_bindir}/amavisd-agent
%{_bindir}/amavisd-nanny
%{_bindir}/amavisd-release
%{_bindir}/amavisd-signer
%{_bindir}/amavisd-submit
%dir %attr(750,amavis,amavis) %{_localstatedir}/spool/amavisd
%dir %attr(750,amavis,amavis) %{_localstatedir}/spool/amavisd/tmp
%dir %attr(750,amavis,amavis) %{_localstatedir}/spool/amavisd/db
%dir %attr(750,amavis,amavis) %{_localstatedir}/spool/amavisd/quarantine
%{_tmpfilesdir}/amavisd-new.conf
%dir %attr(755,amavis,amavis) %{_localstatedir}/run/amavisd
%dir %attr(770,amavis,clamav) %{_localstatedir}/run/clamd.amavisd

%files snmp
%doc AMAVIS-MIB.txt
%{_unitdir}/amavisd-snmp.service
%{_sbindir}/amavisd-snmp-subagent

%files zeromq
%{_unitdir}/amavis-mc.service
%{_sbindir}/amavis-mc
%{_bindir}/amavisd-status
%{_bindir}/amavis-services

%files snmp-zeromq
%{_unitdir}/amavisd-snmp-zmq.service
%{_sbindir}/amavisd-snmp-subagent-zmq
