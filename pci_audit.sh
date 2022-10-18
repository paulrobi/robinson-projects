#!/bin/sh

if [ ! -f /etc/redhat-release ] ; then
   printf "For Centos and Redhat 6,7,8 only. Exiting \n"
   exit 1
fi
osname=`cat /etc/redhat-release|awk '{print $1}'`
osversion=`cat /etc/redhat-release|grep ^VERSION_ID|awk -F'\"' '{print $2}'`
scap_pciprofile="xccdf_org.ssgproject.content_profile_pci-dss"


if [ `cat /etc/redhat-release |grep -i "Red Hat"` ] ; then
   ostype="rhel"
else
   ostype="centos"
fi

osversion=`cat /etc/redhat-release|awk 'BEGIN{FS="release"} /release/ {print $2}'|awk '{print $1}'`
case $osversion in
      8*) osrelease=8
          ;;
      7*) osrelease=7
          ;;
      6*) osrelease=6
          ;;
      *) printf "Error. Unregcognized OS Release. Script supports RHEL/Centos 6,7,8 \n"
         exit 1
         ;;
esac

if ! rpm -qa openscap-scanner ; then
   yum -y install openscap-scanner &> /dev/null
else
   yum -y upgrade openscap-scanner  &> /dev/null
fi

if ! rpm -qa scap-security-guide ; then
   yum -y install scap-security-guide &> /dev/null
else
   yum -y upgrade scap-security-guide &> /dev/null
fi

if [ -d /root/Compliance ] ; then
   cd /root
   /bin/rm -r Compliance
fi

mkdir -p /root/Compliance
chmod 0700 /root/Compliance
cd /root/Compliance

printf "Checking Internet Access to pull the latest..."
curl -I https://google.com &>/dev/null
if [ $? == 0 ] ; then
   printf "Access ok \n"
   printf "Running report "
   trap '[ -z $! ] || kill $!' SIGHUP SIGINT SIGQUIT SIGTERM
   /bin/oscap xccdf eval --profile $scap_pciprofile \
       --results-arf /root/Compliance/`uname -n`-arf.xml \
       --report  /root/Compliance/`uname -n`-report.html \
       --fetch-remote-resources \
       /usr/share/xml/scap/ssg/content/ssg-${ostype}${osrelease}-ds.xml >/dev/null 2>&1 &
   while [ -e /proc/$! ]; do
       echo -n "."
       sleep 5
   done
else
   printf "Access not updating \n"
   printf "Running report "
   trap '[ -z $! ] || kill $!' SIGHUP SIGINT SIGQUIT SIGTERM
   /bin/oscap xccdf eval --profile $scap_pciprofile \
       --results-arf /root/Compliance/`uname -n`-arf.xml \
       --report  /root/Compliance/`uname -n`-report.html \
       --fetch-remote-resources \
       /usr/share/xml/scap/ssg/content/ssg-${ostype}${osrelease}-ds.xml >/dev/null 2>&1 &
   while [ -e /proc/$! ]; do
       echo -n "."
       sleep 5
   done
fi
printf "Complete. Retreive /root/Compliance/`uname -n`-report.html \n"
