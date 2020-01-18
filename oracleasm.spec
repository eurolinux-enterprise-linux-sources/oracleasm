%define kmod_name		oracleasm
%define kmod_driver_version	2.0.8
%define kmod_rpm_release	21
%define kmod_git_hash		73eec1df4b6aec6e850db5015d74dbf6dee01e01
%define kmod_kernel_version	3.10.0-862.el7
%define kernel_version		3.10.0-862.el7
%define kmod_kbuild_dir		drivers/block/oracleasm


%{!?dist: %define dist .el7}

Source0:	%{kmod_name}-%{kmod_driver_version}.tar.bz2
Source1:	%{kmod_name}.files
Source2:	depmodconf
Source3:	find-requires.ksyms
Source4:	find-provides.ksyms
Source5:	kmodtool
Source6:	symbols.greylist-x86_64
Source7:	oracleasm.preamble

Patch0:         oracleasm.patch
Patch1:         classify-device-connectivity-issues-as-global-errors.patch

%define __find_requires %_sourcedir/find-requires.ksyms
%define __find_provides %_sourcedir/find-provides.ksyms %{kmod_name} %{?epoch:%{epoch}:}%{version}-%{release}

Name:		%{kmod_name}
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	%{kmod_name} kernel module

Group:		System/Kernel
License:	GPLv2
URL:		http://www.kernel.org/
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	%kernel_module_package_buildreqs
ExclusiveArch:  x86_64


# Build only for standard kernel variant(s); for debug packages, append "debug"
# after "default" (separated by space)
%kernel_module_package -s %{SOURCE5} -f %{SOURCE1} -p %{SOURCE7} default

%description
%{kmod_name} - driver update

%prep
%setup
%patch0 -p1
%patch1 -p1

set -- *
mkdir source
mv "$@" source/
cp %{SOURCE6} source/
mkdir obj

%build
for flavor in %flavors_to_build; do
	rm -rf obj/$flavor
	cp -r source obj/$flavor

	# update symvers file if existing
	symvers=source/Module.symvers-%{_target_cpu}
	if [ -e $symvers ]; then
		cp $symvers obj/$flavor/%{kmod_kbuild_dir}/Module.symvers
	fi

	make -C %{kernel_source $flavor} M=$PWD/obj/$flavor/%{kmod_kbuild_dir} \
		NOSTDINC_FLAGS="-I $PWD/obj/$flavor/include"

	# mark modules executable so that strip-to-file can strip them
	find obj/$flavor/%{kmod_kbuild_dir} -name "*.ko" -type f -exec chmod u+x '{}' +
done

%{SOURCE2} %{name} %{kmod_kernel_version} obj > source/depmod.conf

greylist=source/symbols.greylist-%{_target_cpu}
if [ -f $greylist ]; then
	cp $greylist source/symbols.greylist
else
	touch source/symbols.greylist
fi

if [ -d source/firmware ]; then
	make -C source/firmware
fi

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{name}
for flavor in %flavors_to_build ; do
	make -C %{kernel_source $flavor} modules_install \
		M=$PWD/obj/$flavor/%{kmod_kbuild_dir}
	# Cleanup unnecessary kernel-generated module dependency files.
	find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;
done

install -m 644 -D source/depmod.conf $RPM_BUILD_ROOT/etc/depmod.d/%{kmod_name}.conf
install -m 644 -D source/symbols.greylist $RPM_BUILD_ROOT/usr/share/doc/kmod-%{kmod_name}/greylist.txt

if [ -d source/firmware ]; then
	make -C source/firmware INSTALL_PATH=$RPM_BUILD_ROOT INSTALL_DIR=updates install
fi

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Feb 22 2018 Petr Oros <poros@redhat.com> 2.0.8-21
- For >= kernel-3.10.0-855.el7
- Resolves: #1498103

* Tue Nov 14 2017 Petr Oros <poros@redhat.com> 2.0.8-20
- For >= kernel-3.10.0-783.el7
- Resolves: #1498103

* Mon Jun 26 2017 Petr Oros <poros@redhat.com> 2.0.8-19
- For >= kernel-3.10.0-685.el7
- Resolves: #1441193

* Thu Apr 13 2017 Petr Oros <poros@redhat.com> 2.0.8-18
- For >= kernel-3.10.0-650.el7
- Resolves: #1441193

* Mon Sep 26 2016 Petr Oros <poros@redhat.com> 2.0.8-17
- For >= kernel-3.10.0-510.el7
- Resolves: #1354376

* Mon Jul 11 2016 Petr Oros <poros@redhat.com> 2.0.8-16
- For >= kernel-3.10.0-461.el7
- Resolves: #1354376

* Mon Oct 26 2015 Petr Oros <poros@redhat.com> 2.0.8-15
- For >= kernel-3.10.0-326.el7
- Resolves: #1265218

* Tue Sep 22 2015 Petr Oros <poros@redhat.com> 2.0.8-14
- Classify device connectivity issues as global errors
- For >= kernel-3.10.0-319.el7
- Resolves: #1265218

* Wed Sep 9 2015 Petr Oros <poros@redhat.com> 2.0.8-13
- rebuild for >= kernel-3.10.0-315.el7
- Resolves: #1245327

* Thu Sep 3 2015 Petr Oros <poros@redhat.com> 2.0.8-12
- rebuild for kernel-3.10.0-313.el7
- Resolves: #1245327

* Wed Aug 19 2015 Petr Oros <poros@redhat.com> 2.0.8-11
- rebuild for kernel-3.10.0-306.0.1.el7
- Resolves: #1245327

* Tue Aug 18 2015 Petr Oros <poros@redhat.com> 2.0.8-10
- rebuild for kernel-3.10.0-306.el7
- Resolves: #1245327

* Tue Aug 4 2015 Petr Oros <poros@redhat.com> 2.0.8-9
- rebuild for kernel-3.10.0-302.el7
- Resolves: #1245327

* Fri Jan 30 2015 Dave Anderson <anderson@redhat.com> 2.0.8-8
- rebuild for kernel-3.10.0-229.el7

* Wed Jan 28 2015 Jan Blazek <jblazek@redhat.com> 2.0.8-7
- rebuild for kernel-3.10.0-227.el7

* Mon Dec 1 2014 Weiping Pan <wpan@redhat.com> 2.0.8 5
- build oracleasm for 7.0.z, 
- codes from git://oss.oracle.com/git/linux-uek3-3.8.git,
- commit 73eec1df4b6aec6e850db5015d74dbf6dee01e01
- patch0 is to replace create_proc_entry with proc_create.

* Wed Aug 20 2014 Weiping Pan <wpan@redhat.com> 2.0.8 2
- rebuild oracleasm for RHEL6.4 in brew, update the version tp 2.0.8-2

* Mon Aug 11 2014 Weiping Pan <wpan@redhat.com> 2.0.8.rh64 1
- rebuild oracleasm for RHEL6.4, update the version tp 2.0.8.rh64-1

* Tue Jul 15 2014 Weiping Pan <wpan@redhat.com> 2.0.8.rh1 2
- rebuild oracleasm for RHEL6.4, sync to upstream commit d368091e98dc
- (oracleasm: Add support for new error return codes from block/SCSI)

* Fri Jan 24 2014 Weiping Pan <wpan@redhat.com> 2.0.8.rh1 1
- rebuild oracleasm for RHEL6.5

* Tue Jan 29 2013 Jiri Benc <jbenc@redhat.com> 2.0.6.rh1 2
- providing oracleasm to be compatible with oracleasmlib builds

* Thu Jan 24 2013 Jiri Benc <jbenc@redhat.com> 2.0.6.rh1 1
- updated to a newer version with some fixes

* Fri Sep  2 2011 Jiri Olsa <jolsa@redhat.com> 2.0.6 5
- kernel version fix

* Tue Aug 30 2011 Jiri Olsa <jolsa@redhat.com> 2.0.6 4
- kernel version fix

* Tue Aug 30 2011 Jiri Olsa <jolsa@redhat.com> 2.0.6 3
- kernel version fix

* Tue Aug 30 2011 Jiri Olsa <jolsa@redhat.com> 2.0.6 2
- removed kmod- prefix

* Tue Jul 19 2011 Jiri Olsa <jolsa@redhat.com> 2.0.6 1
- oracleasm DUP module
