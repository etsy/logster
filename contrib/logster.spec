%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           logster
Version:        1.0.1
Release:        1%{?dist}
Summary:        Parse log files, generate metrics for Graphite and Ganglia

Group:          Applications/System
License:        GPLv3
URL:            https://github.com/etsy/logster
Source0:        https://github.com/etsy/logster/archive/master.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       logcheck,python

%description
Logster is a utility for reading log files and generating metrics in Graphite
or Ganglia. It is ideal for visualizing trends of events that are occurring in
your application/system/error logs.


%prep
%setup -q -n logster-master


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/logster
%{python_sitelib}/*


%changelog
