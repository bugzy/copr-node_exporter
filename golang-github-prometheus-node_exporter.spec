# Run tests (requires network connectivity)
%global with_check 0

# Prebuilt binaries break build process for CentOS. Disable debug packages to resolve
%if 0%{?rhel}
%define debug_package %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         prometheus
%global repo            node_exporter
# https://github.com/prometheus/node_exporter/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0.18.1
Release:        2%{?dist}
Summary:        Exporter for machine metrics
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz
Source1:        node_exporter.service
Source2:        sysconfig.node_exporter

Provides:       node_exporter = %{version}-%{release}

%if 0%{?rhel} != 6
BuildRequires:  systemd
%endif

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels.

%prep
%setup -q -n %{repo}-%{version}

%build
export GO111MODULE=on
go build -ldflags=-linkmode=external -mod vendor -o node_exporter

%install
%if 0%{?rhel} != 6
install -d -p   %{buildroot}%{_unitdir}
%endif

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/node_exporter/node_exporter.conf
install -Dpm 0755 node_exporter %{buildroot}%{_sbindir}/node_exporter
%if 0%{?rhel} != 6
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/node_exporter.service
%endif

%if 0%{?with_check}
%check
export GO111MODULE=on
go test -mod vendor
%endif


%files
%if 0%{?rhel} != 6
%{_unitdir}/node_exporter.service
%endif
%attr(0640, node_exporter, node_exporter) %config(noreplace) %{_sysconfdir}/node_exporter/node_exporter.conf
%license LICENSE
%doc README.md
%attr(0755, root, root) %caps(cap_net_raw=ep) %{_sbindir}/node_exporter

%pre
getent group node_exporter > /dev/null || groupadd -r node_exporter
getent passwd node_exporter > /dev/null || \
    useradd -Mrg node_exporter -s /sbin/nologin \
            -c "MySQL Prometheus exporter" node_exporter

%post
%if 0%{?rhel} != 6
%systemd_post node_exporter.service
%endif

%preun
%if 0%{?rhel} != 6
%systemd_preun node_exporter.service
%endif

%postun
%if 0%{?rhel} != 6
%systemd_postun node_exporter.service
%endif

%changelog
* Thu Nov 21 2019 Bugzy Little <bugzylittle@gmail.com> - 0.18.1-2
- Fix default config file location in systemd unit file

* Thu Nov 21 2019 Bugzy Little <bugzylittle@gmail.com> - 0.18.1-1
- Initial package

