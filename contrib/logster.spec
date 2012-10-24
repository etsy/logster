%define __prefix /usr/local

Summary:       Parse log files, generate metrics for Graphite and Ganglia
Name:          logster
Version:       0.0.1
Release:       1%{?dist}
Group:         MAILRU
License:       LGPL
Url:           https://github.com/etsy/logster
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:     noarch
Requires:      logcheck


%description
Parse log files, generate metrics for Graphite and Ganglia


%prep
# clean build directory
%{__rm} -rf %{buildroot}%{__prefix}/logster


%build
# clone repo
git clone --depth=1 https://github.com/dreadatour/logster.git %{buildroot}%{__prefix}/logster

# clean repository files
%{__rm} -rf %{buildroot}%{__prefix}/logster/{.git,.gitignore,.travis.yml,Makefile,README.md,setup.py,tests}

# create directory for logs
%{__mkdir} -p %{buildroot}/var/log/logster


%install
chmod +x %{buildroot}%{__prefix}/logster/bin/*


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{__prefix}/logster/
/var/log/logster/
