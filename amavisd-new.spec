Summary:	A Mail Virus Scanner
Name:		amavisd-new
Version:	2.8.0
Release:	1
License:	GPL
Group:		Networking/Mail
URL:		http://www.ijs.si/software/amavisd/
Source0:	http://www.ijs.si/software/amavisd/%{name}-%{version}.tar.gz
Patch0:		amavisd-new-2.4.5-init.patch
Patch1:		amavisd-new-mdv_conf.diff
Patch2:		amavisd-new-mdv_conf-2.diff
Patch3:		amavisd-new-2.6.4-SA.patch
Patch4:		amavisd-new-2.6.4-snmp.patch
Requires:	file >= 4.21
# http://archives.mandrivalinux.com/cooker/2005-06/msg01987.php
Requires:	mail-server
Requires:	perl-Archive-Tar
Requires:	perl-Archive-Zip
Requires:	perl-BerkeleyDB
Requires:	perl(Compress::Zlib)
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

%description
AMaViS is a perl script that interfaces a Mail Transport Agent (MTA)
with one or more virus scanners (not provided).

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1 -b .init
%patch2 -p1 -b .confpch
%patch3 -p1 -b .SA
%patch4 -p1 -b .SNMP
%build

%install

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/amavisd
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}/var/lib/amavis/.spamassassin
install -d %{buildroot}/var/spool/amavis/virusmails
install -d %{buildroot}/var/lib/amavis/{tmp,db}

install -m0755 amavisd_init.sh %{buildroot}%{_initrddir}/amavisd
install -m0640 amavisd.conf %{buildroot}%{_sysconfdir}/amavisd/amavisd.conf
install -m0640 amavisd.conf-default %{buildroot}%{_sysconfdir}/amavisd/amavisd.conf-default
install -m0755 amavisd %{buildroot}%{_sbindir}/amavisd
install -m0755 p0f-analyzer.pl %{buildroot}%{_sbindir}/
install -m0755 amavisd-agent %{buildroot}%{_sbindir}/
install -m0755 amavisd-nanny %{buildroot}%{_sbindir}/
install -m0755 amavisd-release %{buildroot}%{_sbindir}/
install -m0755 amavisd-snmp-subagent %{buildroot}%{_sbindir}/


cat > %{buildroot}/var/lib/amavis/.spamassassin/user_prefs <<EOF
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

%pre
%_pre_useradd amavis /var/lib/amavis /bin/false
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
%doc AMAVIS-MIB.txt
%attr(0755,root,root) %{_initrddir}/amavisd
%attr(0640,root,amavis) %config(noreplace) %{_sysconfdir}/amavisd/amavisd.conf
%attr(0640,root,amavis) %{_sysconfdir}/amavisd/amavisd.conf-default
%attr(0755,root,root) %{_sbindir}/amavisd
%attr(0755,root,root) %{_sbindir}/p0f-analyzer.pl
%attr(0755,root,root) %{_sbindir}/amavisd-agent
%attr(0755,root,root) %{_sbindir}/amavisd-nanny
%attr(0755,root,root) %{_sbindir}/amavisd-release
%attr(0755,root,root) %{_sbindir}/amavisd-snmp-subagent
%attr(0755,root,root) %{_bindir}/amavisd-*
%attr(0755,root,root) %dir /var/spool/amavis
%attr(0750,amavis,amavis) %dir /var/spool/amavis/virusmails
%attr(0750,amavis,amavis) %dir /var/lib/amavis
%attr(0750,amavis,amavis) %dir /var/lib/amavis/tmp
%attr(0750,amavis,amavis) %dir /var/lib/amavis/db
%attr(0750,amavis,amavis) %dir /var/lib/amavis/.spamassassin
%attr(0640,amavis,amavis) %config(noreplace) /var/lib/amavis/.spamassassin/user_prefs


%changelog
* Thu Jul 14 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.7.0-1
+ Revision: 690018
- 2.7.0

* Fri May 20 2011 Nicolas LÃ©cureuil <nlecureuil@mandriva.com> 2.6.6-2
+ Revision: 676312
- Clean spec file for rpm5

* Fri May 20 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.6.6-1
+ Revision: 676263
- 2.6.6
  P2 rediffed

* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 2.6.4-9
+ Revision: 662764
- mass rebuild

  + Luis Daniel Lucio Quiroz <dlucio@mandriva.org>
    - Rebuild

* Wed Jul 28 2010 JÃ©rÃ´me Quelin <jquelin@mandriva.org> 2.6.4-7mdv2011.0
+ Revision: 562412
- perl 5.12.1 rebuild

* Sun Feb 21 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.6.4-6mdv2010.1
+ Revision: 509140
- New P3 & P4, more options to amavisd

* Sat Nov 21 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.6.4-5mdv2010.1
+ Revision: 467801
- New P2, comment P1 (temporal) as fix for BUG #14838

* Tue Nov 10 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.6.4-4mdv2010.1
+ Revision: 464261
- P2 already done, ereased
- P2 to fix amavisd-nanny db path

* Wed Jul 22 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 2.6.4-3mdv2010.0
+ Revision: 398516
- SNMP new scripts and docs were not packaged

* Sun Jun 28 2009 Oden Eriksson <oeriksson@mandriva.com> 2.6.4-2mdv2010.0
+ Revision: 390182
- fix deps, perl(Compress::Zlib) somehow moved into perl-IO-Compress

* Sat Jun 27 2009 Oden Eriksson <oeriksson@mandriva.com> 2.6.4-1mdv2010.0
+ Revision: 389815
- 2.6.4
- rediffed P1

* Thu Mar 12 2009 Oden Eriksson <oeriksson@mandriva.com> 2.6.2-2mdv2009.1
+ Revision: 354199
- added changes by Giuseppe Ghib?\195?\131?\194?\178 in P1

* Sun Mar 08 2009 Oden Eriksson <oeriksson@mandriva.com> 2.6.2-1mdv2009.1
+ Revision: 352799
- 2.6.2
- rediffed P1
- drop the logrotation due to poor support, syslog logging is
  the preferred way according to upstream author

* Mon Aug 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.6.1-3mdv2009.0
+ Revision: 273232
- restore the init script
- fix #42875 (amavisd doesn't start because of missing /var/log/amavisd)

* Tue Jul 29 2008 Oden Eriksson <oeriksson@mandriva.com> 2.6.1-2mdv2009.0
+ Revision: 252238
- hardcode %%{_localstatedir}

* Mon Jun 30 2008 Oden Eriksson <oeriksson@mandriva.com> 2.6.1-1mdv2009.0
+ Revision: 230335
- 2.6.1

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Thu Apr 24 2008 Oden Eriksson <oeriksson@mandriva.com> 2.6.0-1mdv2009.0
+ Revision: 197171
- 2.6.0
- rediffed P1
- fix deps

* Fri Mar 14 2008 Oden Eriksson <oeriksson@mandriva.com> 2.5.4-1mdv2008.1
+ Revision: 187826
- 2.5.4
- rediffed P1

* Fri Jan 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.5.3-3mdv2008.1
+ Revision: 154635
- revert changes

* Fri Jan 18 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.5.3-2mdv2008.1
+ Revision: 154614
- drop useless explicit perl dependencies
- make compression utilities optional dependencies
- drop unused plf build options

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Dec 13 2007 Oden Eriksson <oeriksson@mandriva.com> 2.5.3-1mdv2008.1
+ Revision: 119283
- 2.5.3

  + Thierry Vignaud <tv@mandriva.org>
    - fix URL

* Wed Aug 22 2007 Oden Eriksson <oeriksson@mandriva.com> 2.5.2-1mdv2008.0
+ Revision: 69140
- 2.5.2
- renumber patches
- rediffed the mdv_conf patch
- conform to the 2008 specs (don't start it per default)

  + Giuseppe GhibÃ² <ghibo@mandriva.com>
    - Release 2.5.2.
    - Rebuilt Patch11.

* Mon Jun 04 2007 Oden Eriksson <oeriksson@mandriva.com> 2.5.1-1mdv2008.0
+ Revision: 35020
- 2.5.1
- rediffed P11
- fixed deps

* Thu May 17 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.4.5-5mdv2008.0
+ Revision: 27592
- Redid init patch: add LSB support, don't be too verbose.

* Tue May 08 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2.4.5-4mdv2008.0
+ Revision: 25349
- Fix path of clamd socket in default amavisd.conf file provided
  (mdv_conf patch). Reported by Colin Guthrie on ticket #30536.


* Tue Feb 27 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 2.4.5-3mdv2007.1
+ Revision: 126526
- Bump release to 3.
- Added perl-ldap to Requires.
- Specify release >= 1.08 for Requires: perl-Convert-UUlib.

* Tue Feb 27 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 2.4.5-2mdv2007.1
+ Revision: 126484
- Bumped release to 2.
- Removed Patch13 (no longer needed). Thanks to Pixel for
  having spotted this (fix bug #28725).

* Fri Feb 09 2007 Giuseppe GhibÃ² <ghibo@mandriva.com> 2.4.5-1mdv2007.1
+ Revision: 118648
- Import amavisd-new

* Fri Feb 09 2007 Giuseppe Ghibò <ghibo@mandriva.com> 2.4.5-1mdv2007.1
- Release 2.4.5.
- Rediff Patch11.

* Tue Aug 29 2006 Giuseppe Ghibò <ghibo@mandriva.com> 2.4.2-4mdv2007.0
- Fixed %%{rel} for plf.
- removed use_dcc into default user_prefs (no longer supported).
- commented auto_learn into default user_prefs (this option became bayes_auto_learn and 
  by default is already enabled).

* Thu Jul 27 2006 Giuseppe Ghibò <ghibo@mandriva.coM> 2.4.2-3mdv2007.0
- Remerge Patch12 into Patch11.

* Thu Jul 27 2006 Giuseppe Ghibò <ghibo@mandriva.com> 2.4.2-2mdv2007.0
- Fixed Patch11 for problem with clamav (socket was in the wrong dir)
  and merged with Patch12.
- Removed patch2.

* Thu Jun 29 2006 Oden Eriksson <oeriksson@mandriva.com> 2.4.2-1mdv2007.0
- 2.4.2
- rediffed patches; P11

* Thu Jun 01 2006 Oden Eriksson <oeriksson@mandriva.com> 2.4.1-1mdv2007.0
- 2.4.1
- rediffed patches; P11,P13
- added some tools to the package
- fix deps

* Tue Oct 11 2005 Giuseppe Ghibò <ghibo@mandriva.com> 2.3.3-1mdk
- Release: 2.3.3.
- Rebuilt Patch12.

* Thu Aug 25 2005 Andreas Hasenack <andreas@mandriva.com> 2.3.2-5mdk
- fixed aliases handling in %%post to cope with postfix/others
  (mta test stolen from mailman, by Guillaume.Rousse@inria.fr)

* Thu Aug 25 2005 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-4mdk
- fix deps
- fix #17288

* Fri Aug 12 2005 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-3mdk
- correct the rpm-helper deps

* Thu Aug 11 2005 Nicolas Lécureuil <neoclust@mandriva.org> 2.3.2-2mdk
- fix rpmlint errors (PreReq)

* Sat Aug 06 2005 Giuseppe Ghibò <ghibo@mandriva.com> 2.3.2-1mdk
- Release: 2.3.2.
- Rebuilt Patch11, Patch12, Patch13.

* Tue Jul 19 2005 Andreas Hasenack <andreas@mandriva.com> 2.2.1-4mdk
- changed requires: s/smtpdaemon/mail-server/ (see
  http://archives.mandrakelinux.com/cooker/2005-06/msg01987.php and
  http://archives.mandrakelinux.com/cooker/2005-06/msg01987.php)

* Thu Jul 07 2005 Oden Eriksson <oeriksson@mandriva.com> 2.2.1-3mdk
- added rediffed P13 from the openpkg kolab2 packages

* Tue Mar 15 2005 Oden Eriksson <oden.eriksson@kvikkjokk.net> 2.2.1-2mdk
- fix deps
- rpmlint fixes

* Thu Dec 23 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 2.2.1-1mdk
- Release: 2.2.1.
- Rebuilt Patch11.
- Rebuilt Patch12.
- Added pax, ripmime, freeze to Requires.

* Fri Sep 24 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 2.1.2-1mdk
- Release: 2.1.3.
- Rebuilt Patch10.
- Rebuilt Patch11.
- Rebuilt Patch12.
- Added mthredir, sdboot.gen, funlove, yaha, zafi, gibe, lovgate, nyxem,
  mabutu, plexus to list of viruses that fake sender maps.

* Fri Jul 30 2004 Lenny Cartier <lenny@mandrakesoft.com> 0.20040701-1mdk
- updated to 20040701 by Andre Nathan <andre@digirati.com.br>

* Mon Mar 22 2004 Giuseppe Ghibò <ghibo@mandrakesoft.com> 0.20030616-18mdk
- Updated to release 20030616p8.
- Added bagle to fakesender virus list.
- Rebuilt Patch11, Patch13.

