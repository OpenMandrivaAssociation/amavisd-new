Summary:	A Mail Virus Scanner
Name:		amavisd-new
Version:	2.6.0
Release:	%mkrel 1
License:	GPL
Group:		Networking/Mail
URL:		http://www.ijs.si/software/amavisd/
Source0:	http://www.ijs.si/software/amavisd/%{name}-%{version}.tar.gz
Patch0:		amavisd-new-2.4.5-init.patch
Patch1:		amavisd-new-mdv_conf.diff
Patch2:		amavisd-new-2008_specs.diff
Requires:	file >= 4.21
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires:	mail-server
Requires:	perl-Archive-Tar
Requires:	perl-Archive-Zip
Requires:	perl-BerkeleyDB
Requires:	perl-Compress-Zlib
Requires:	perl-Convert-TNEF
Requires:	perl-Convert-UUlib >= 1.08
Requires:	perl-Crypt-OpenSSL-RSA
Requires:	perl-DBI
Requires:	perl-Digest-MD5
Requires:	perl-IO-stringy
Requires:	perl-ldap
Requires:	perl-libnet
Requires:	perl-Mail-DKIM
Requires:	perl-Mail-SpamAssassin
Requires:	perl-MailTools
Requires:	perl-MIME-Base64
Requires:	perl-MIME-tools >= 5.411
Requires:	perl-Net-Server >= 0.84
Requires:	perl-Razor-Agent
Requires:	perl-Time-HiRes
Requires:	perl-Unix-Syslog
Requires:	spamassassin >= 2.60
Requires:	spamassassin-spamd >= 2.60
Requires:	spamassassin-spamc >= 2.60
Requires:	binutils
Requires:	bzip2
Requires:	cabextract
Requires:	tnef
Requires:	lha
Requires:	lzop
Requires:	ncompress
Requires:	nomarch
Requires:	pax
Requires:	ripole
Provides:	amavisd
BuildArch:	noarch
# this is for serviceadd, etc.
Requires(post): rpm-helper
Requires(preun): rpm-helper
# this is for useradd, groupadd, etc.
Requires(pre): rpm-helper
Requires(postun): rpm-helper
#PreReq:	clamav
Obsoletes:	amavis-postfix
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
AMaViS is a perl script that interfaces a Mail Transport Agent (MTA)
with one or more virus scanners (not provided).

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1 -b .init
%patch1 -p1 -b .confpch
%patch2 -p0 -b .2008_specs

%build

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/amavisd
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_localstatedir}/lib/amavis/.spamassassin
install -d %{buildroot}/var/spool/amavis/virusmails
install -d %{buildroot}%{_localstatedir}/lib/amavis/{tmp,db}

install -m0755 amavisd_init.sh %{buildroot}%{_initrddir}/amavisd
install -m0640 amavisd.conf %{buildroot}%{_sysconfdir}/amavisd/amavisd.conf
install -m0640 amavisd.conf-default %{buildroot}%{_sysconfdir}/amavisd/amavisd.conf-default
install -m0640 amavisd.conf-sample %{buildroot}%{_sysconfdir}/amavisd/amavisd.conf-sample
install -m0755 amavisd %{buildroot}%{_sbindir}/amavisd
install -m0755 p0f-analyzer.pl %{buildroot}%{_sbindir}/
install -m0755 amavisd-agent %{buildroot}%{_sbindir}/
install -m0755 amavisd-nanny %{buildroot}%{_sbindir}/
install -m0755 amavisd-release %{buildroot}%{_sbindir}/

cat > %{buildroot}%{_localstatedir}/lib/amavis/.spamassassin/user_prefs <<EOF
# SpamAssassin User Preferences file
# (see perldoc Mail::SpamAssassin::Conf for details of what can be tweaked).
# Note that the entries for headers won't have effect, since those are
# directly handled/overridden by amavisd and amavisd.conf.

dns_available yes

# Bayes filters requires at least 200 entries of spam and 200 of ham 
# for start working
bayes_file_mode 0640
use_bayes 1
#bayes_auto_learn 0

skip_rbl_checks 1
use_razor2 0
use_pyzor 0
#dcc_add_header 1

# Custom scores (local|net|bayes|bayes+net)
#score   BAYES_99        4.300 4.300 5.400 5.400
#score   BAYES_90        3.500 3.500 3.500 3.500
#score   BAYES_80        3.000 3.000 3.000 3.000
#score   DCC_CHECK       4.000 4.000 4.000 4.000
#score   RAZOR2_CHECK    2.500 2.500 2.500 2.500
#score   HABEAS_SWE      -0.01
EOF

cat > %{buildroot}%{_bindir}/amavisd-checkbayesdb <<EOF
#!/bin/sh
su amavis -c "%{_bindir}/sa-learn --dump" -s /bin/sh
EOF

cat > %{buildroot}%{_bindir}/amavisd-checkcfg <<EOF
#!/bin/sh
su amavis -c "%{_bindir}/spamassassin --lint -D" -s /bin/sh
EOF

cat > %{buildroot}%{_bindir}/amavisd-mboxlearnham <<EOF
#!/bin/sh
su amavis -c "%{_bindir}/sa-learn --showdots --ham --mbox \$1" -s /bin/sh
EOF

cat > %{buildroot}%{_bindir}/amavisd-mboxlearnspam <<EOF
#!/bin/sh
su amavis -c "%{_bindir}/sa-learn --showdots --spam --mbox \$1" -s /bin/sh
EOF

%clean
rm -rf %{buildroot}

%pre
%_pre_useradd amavis %{_localstatedir}/lib/amavis /bin/false
%_pre_groupadd amavis amavis,clamav

%post
%_post_service amavisd

# check mta
mta="`readlink /etc/alternatives/sendmail-command 2>/dev/null | cut -d . -f 2`"
if [ "$mta" = "postfix" ]; then
	aliases="%{_sysconfdir}/postfix/aliases"
else
	aliases="%{_sysconfdir}/aliases"
fi
if [ -e "$aliases" ]; then
	grep -q "virusalert" "$aliases" || \
		echo "virusalert: root" >> "$aliases"
	[ -x %{_bindir}/newaliases ] && %{_bindir}/newaliases > /dev/null 2>&1
fi

if [ -x /usr/sbin/postconf ] && [ -z `/usr/sbin/postconf -h content_filter` ]; then
	postconf -e content_filter=lmtp-filter:127.0.0.1:10025
	postconf -e receive_override_options=no_address_mappings
fi

%preun
%_preun_service amavisd

%files
%defattr(-,root,root)
%doc AAAREADME.first INSTALL LICENSE README_FILES RELEASE_NOTES test-messages
%doc LDAP.schema amavisd-new-courier.patch amavisd-new-qmqpqq.patch
%attr(0755,root,root) %{_initrddir}/amavisd
%attr(0640,root,amavis) %config(noreplace) %{_sysconfdir}/amavisd/amavisd.conf
%attr(0640,root,amavis) %{_sysconfdir}/amavisd/amavisd.conf-default
%attr(0640,root,amavis) %{_sysconfdir}/amavisd/amavisd.conf-sample
%attr(0755,root,root) %{_sbindir}/amavisd
%attr(0755,root,root) %{_sbindir}/p0f-analyzer.pl
%attr(0755,root,root) %{_sbindir}/amavisd-agent
%attr(0755,root,root) %{_sbindir}/amavisd-nanny
%attr(0755,root,root) %{_sbindir}/amavisd-release
%attr(0755,root,root) %{_bindir}/amavisd-*
%attr(0755,root,root) %dir /var/spool/amavis
%attr(0750,amavis,amavis) %dir /var/spool/amavis/virusmails
%attr(0750,amavis,amavis) %dir %{_localstatedir}/lib/amavis
%attr(0750,amavis,amavis) %dir %{_localstatedir}/lib/amavis/tmp
%attr(0750,amavis,amavis) %dir %{_localstatedir}/lib/amavis/db
%attr(0750,amavis,amavis) %dir %{_localstatedir}/lib/amavis/.spamassassin
%attr(0640,amavis,amavis) %config(noreplace) %{_localstatedir}/lib/amavis/.spamassassin/user_prefs
