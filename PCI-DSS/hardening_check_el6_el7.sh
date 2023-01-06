#!/bin/bash

################################################################################
#
# EL7 hardening checks
#
################################################################################


################################################################################
#
# Changelog
#
# 2022-11-03: D. Eckert (v1.0.0)

#	* Initial release
#
#	- Basic functionality based on "2022 Hardening Checks" Google Sheet
#
################################################################################

#
# some "print" aliases for easy putput formatting
#
PRINT1="printf %-70s"          # left-justified, padded to 70 characters, no newline 
PRINT2="printf %s\n"           # for [PASS/FAIL]
PRINT3="printf \t%s\n"         # TAB'd in for informational text

################################################################################
#
# Script execution info
#

clear

if [ `rpm -qa | grep -c redhat-release` -ne 0 ]; then
  OS="redhat"
elif [ `rpm -qa | grep -c centos-release` -ne 0 ]; then
  OS="centos"
else
  ${PRINT2} "This script is meant to run on RHEL or CentOS only"
  exit 1
fi

#
# Kernel version is more reliable way to determins major version
#
case `uname -r | awk -F- '{ print $1 }'` in
  "2.6.32")	OSVER=6
		;;
  "3.10.0")	OSVER=7
		;;
  "4.18.0")	OSVER=8
		;;
  *)		${PRINT2} "This script meant for EL6/7/8"
		exit 1
		;;
esac

printf '%s\n' "##################################################"
printf '%s\n' "# Running on: `uname -n`"
printf '%s\n' "# Running on: ${OS} ${OSVER}"
printf '%s\n' "# Running at: `date`"
printf '%s\n' "##################################################"
printf '%s\n' ""

################################################################################
#
# /etc/grub.conf
#
# GRUB/GRUB2 configuration file owner, group and permissions check
#

#
# GRUB config file could be in a few locations based on version and whether
# sysem is BIOS or EFI
#
if [ -f /boot/grub/grub.conf ]; then
  GRUBLOC="/boot/grub/grub.conf"
elif [ -f /boot/grub2/grub.cfg ]; then
  GRUBLOC="/boot/grub2/grub.cfg"
else
  GRUBLOC="/boot/efi/EFI/${OS}/grub.cfg"
fi

${PRINT1} "${GRUBLOC} should be owner:group set to root:root"
GRUB=`ls -l ${GRUBLOC}`
${PRINT2} "[VERIFY]"
${PRINT3} "${GRUB}"

# FMT=`stat --format "%U:%G" ${GRUBLOC}`
# if [ "${FMT}" == "root:root" ]
# then
#   ${PRINT2} "[PASS]"
# else
#   ${PRINT2} "[FAIL] is set to ${FMT}"
# fi

${PRINT1} "${GRUBLOC} permissions should be set to 700"
GRUB=`ls -l ${GRUBLOC}`
${PRINT2} "[VERIFY]"
${PRINT3} "${GRUB}"

# FMT=`stat --format "%a" ${GRUBLOC}`
# if [ "${FMT}" == "700" ]
# then
#   ${PRINT2} "[PASS]"
# else
#   ${PRINT2} "[FAIL] is set to ${FMT}"
# fi

################################################################################
#
# /etc/init.d/functions
#
# Default umask should be 022
#

UMASK=`grep "^umask" /etc/init.d/functions | awk '{ print $2 }'`
${PRINT1} "Default umask should be 022"
if [ "${UMASK}" == "" ]; then
  ${PRINT2} "[FAIL]: Default umask not set"
elif [ "${UMASK}" != "022" ]; then
  ${PRINT2} "[FAIL] is set to ${UMASK}"
else
  ${PRINT2} "[PASS]"
fi

################################################################################
#
# DHCP Server should not be installed
#

${PRINT1} "DHCP Server should not be installed"
rpm -q dhcp >/dev/null 2>&1
if [ $? ]; then
  ${PRINT2} "[PASS]"
else
  ${PRINT2} "[FAIL]"
fi

################################################################################
#
# HTTP Server should not be installed
#

${PRINT1} "HTTP Server should not be installed"
rpm -q httpd >/dev/null 2>&1
if [ $? ]; then
  ${PRINT2} "[PASS]"
else
  ${PRINT2} "[FAIL]"
fi

################################################################################
#
# rsyslog
#

${PRINT1} "rsyslog should be installed"
rpm -q rsyslog >/dev/null 2>&1
if [ $? ]; then
  ${PRINT2} "[PASS]"
else
  ${PRINT2} "[FAIL]"
fi

#
# Checks for initd and systemd systems
#
${PRINT1} "rsyslog should be enabled"
if [ ${OSVER} -eq 6 ]; then
  if [ -f /etc/rc.d/rc3.d/S*syslog ]; then
    ${PRINT2} "[PASS]"
  else
    ${PRINT2} "[FAIL]"
  fi
else
  if [ "`systemctl list-unit-files | grep rsyslog | awk '{ print $NF }'`" == "enabled" ]; then   
     ${PRINT2} "[PASS]"
  else
    ${PRINT2} "[FAIL]"
  fi
fi

${PRINT1} "rsyslog should be configured"
if [ -f /etc/rsyslog.conf ]; then
    ${PRINT2} "[PASS]"
  else
    ${PRINT2} "[FAIL]"
fi

################################################################################
#
# auditd collects login/logout
#

${PRINT1} "audit subsystem collects login/logout events"
if [ `grep -c "logins$" /etc/audit/rules.d/audit.rules` -lt 2 ]; then
  ${PRINT2} "[FAIL]"
  ${PRINT3} "Add the following to /etc/audit/rules.d/audit.rules and restart auditd"
  ${PRINT3} "    -w /var/log/lastlog -p wa -k logins" 
  ${PRINT3} "    -w /var/run/faillock/ -p wa -k logins"
else
  ${PRINT2} "[PASS]"
fi

################################################################################
#
# auditd collects priviledged commands
#

#
# Not a hard-coded list of commands, but find any in the rootfs that have SUID/SGID 'root'
#
# ${PRINT1} "audit subsystem logs priviledged commands"
# ${PRINT2} "[VERIFY]"
# ${PRINT3} "Ensure the following are added to /etc/audit/rules.d/audit.rules, and restart auditd"
# find / -xdev \( -perm -4000 -o -perm -2000 \) -type f | \
# awk '{ print  "-a always,exit -F path=" $1 " -F perm=x -F auid>=1000 -F auid!=4294967295  -k privileged" }' | while read LINE
# do
#   ${PRINT3} "    ${LINE}"
# done

/sbin/auditctl -l

################################################################################
#
# auditd is immutable
#

#
# Once set and auditd restarted, further changes to audit config file(s) requires a reboot
# to take effect
#
${PRINT1} "ensure auditd is immutable"
if [ `grep -v "^$" /etc/audit/rules.d/audit.rules | tail -1 | grep -c "-e 2"` -eq 1 ]; then
  ${PRINT2} "[PASS]"
else
  ${PRINT2} "[FAIL]"
  ${PRINT3} "Ensure the last line of /etc/audit/rules.d/audit.rules is"
  ${PRINT3} "    -e 2"
  ${PRINT3} "and restart auditd"
fi

################################################################################
#
# system file permissions
#

#
# 'stat' command shows file mode "---------" as '0' octal, not '000' - annoying
#
LIST="/etc/passwd:644 /etc/shadow:0 /etc/gshadow:0 /etc/group:644"

for PAIR in ${LIST}
do
  echo ${PAIR} | sed 's/\:/\ /' | while read FILE PERM
  do
    ${PRINT1} "owner:group on ${FILE} set to root:root"
    if [ "`stat --format '%u%g' ${FILE}`" != "00" ]; then
      ${PRINT2} "[FAIL]"
    else
      ${PRINT2} "[PASS]"
    fi

    ${PRINT1} "permissions on ${FILE} set to ${PERM}"
    if [ "`stat --format '%a' ${FILE}`" != "${PERM}" ]; then
      ${PRINT2} "[FAIL]"
    else
      ${PRINT2} "[PASS]"
    fi
  done
done

################################################################################
#
# verify no empty passwords and report any that have empty password
#

${PRINT1} "verify no empty passwords in /etc/shadow"

if [ `cat /etc/shadow | awk -F: '($2 == "" ) { print $1 " does not have a password "}' | wc -l` -gt 0 ]; then
  ${PRINT2} "[FAIL]"
  cat /etc/shadow | awk -F: '($2 == "" ) { print $1 " does not have a password "}' | while read LINE
  do
    ${PRINT3} "${LINE}"
  done
else
  ${PRINT2} "[PASS]"
fi


################################################################################
#
printf '%s\n' ""
