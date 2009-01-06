#Module-Specific definitions
%define mod_name mod_ftpd
%define mod_conf A51_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Apache module for FTP support
Name:		apache-%{mod_name}
Version:	0.14
Release:	%mkrel 7
Group:		System/Servers
License:	Apache License
URL:		http://www.outoforder.cc/projects/apache/mod_ftpd/
Source0: 	http://www.outoforder.cc/downloads/mod_ftpd/%{mod_name}-%{version}.tar.bz2
Source2:	%{mod_conf}
Patch0:		mod_ftpd-dbi_api_fixes.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	libdbi-devel
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_ftpd is a protocol module that allows Apache 2.0 to accept FTP
connections. This allows the FTP component to take advantage of
Apache's authentication system, filters and module support to
easily extend the FTP server.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0

cp %{SOURCE2} %{mod_conf}

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

export CFLAGS="`%{_sbindir}/apxs -q CFLAGS`"

%configure2_5x --localstatedir=/var/lib \
    --with-apxs=%{_sbindir}/apxs \
    --enable-providers=dbm,default,fail,dbi \
    --enable-dbm \
    --enable-default \
    --enable-fail \
    --enable-dbi

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_bindir}

libtool --mode=install %{_bindir}/install mod_ftpd.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftpd.la
libtool --mode=install %{_bindir}/install providers/dbm/mod_ftpd_dbm.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftpd_dbm.la
libtool --mode=install %{_bindir}/install providers/dbi/mod_ftpd_dbi.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftpd_dbi.la
libtool --mode=install %{_bindir}/install providers/default/mod_ftpd_default.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftpd_default.la
libtool --mode=install %{_bindir}/install providers/fail/mod_ftpd_fail.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftpd_fail.la
install -m0755 providers/dbm/dbmchroot %{buildroot}%{_bindir}/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# cleanup
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.*a

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc docs/*.html AUTHORS ChangeLog LICENSE NOTICE README TODO
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_bindir}/dbmchroot
%attr(0755,root,root) %{_libdir}/apache-extramodules/*.so
