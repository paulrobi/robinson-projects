#!/bin/sh
#pci check script 10/31/2022
#paul.robinson@dowjones.com

HOSTNAME=`uname -n`
output=$HOSTNAME-pci-report.txt
DATE=`date`
sshconfigfile="/etc/ssh/sshd_config"

function show_osfiles()
{
 printf "\n" >> $output
 printf "FILE: /etc/passwd \n" >> $output 
 cat /etc/passwd >> $output
 printf "**********************************\n" >> $output
 printf "**********************************\n" >> $output
 printf "\n" >> $output
 printf "FILE: /etc/group \n" >> $output 
 cat /etc/group >> $output 2>&1
 printf "**********************************\n" >> $output
 printf "**********************************\n" >> $output
 printf "FILE: /etc/sudoers \n" >> $output 
 #cat /etc/sudoers |grep -v '^[[:space:]]*$' |egrep -v ^"#|^%|^ALL|^Defaults" >> $output
 cat /etc/sudoers |grep -v '^[[:space:]]*$' |egrep -v ^"#" >> $output
 printf "**********************************\n" >> $output
 printf "**********************************\n" >> $output
 printf "\n" >> $output
 printf "FILE: /etc/sudoers.d/* \n" >> $output 
 ls -l  /etc/sudoers.d/* >> $output
 for file in `ls  /etc/sudoers.d/*`
 do
   printf "OUTPUT: cat $file |grep -v '^[[:space:]]*$' \n" >> $output
   #cat $file |grep -v '^[[:space:]]*$' |egrep -v ^"#|^%|^ALL|^Defaults" >> $output
   cat $file |grep -v '^[[:space:]]*$' |egrep -v ^"#" >> $output
 done
}

function user_sudo_perms()
{
for user in `cat /etc/sudoers |grep -v '^[[:space:]]*$' |egrep -v ^"#|^ALL|^Defaults"|grep ^[a-z,A-Z] |awk '{print $1}'`
do
   printf "OUTPUT:chage -l $user |grep 'Last password change' sudo users last passwd change  \n" >> $output 
   chage -l $user |grep "Last password change" >> $output 2>&1
   printf "\n" >> $output
done
for file in `ls /etc/sudoers.d/*`
do
   for user in `cat $file |grep -v '^[[:space:]]*$' |egrep -v ^"#|^ALL|^Defaults"|grep ^[a-z,A-Z] |awk '{print $1}'`
   do
      printf "OUTPUT:chage -l $user |grep 'Last password change' sudo users last passwd change  \n" >> $output 
      chage -l $user |grep "Last password change" >> $output 2>&1
      printf "\n" >> $output
   done
done
}


cat /dev/null > $output
printf "$HOSTNAME \t $DATE ##################### \n" >> $output
printf "################################################################### \n" >> $output
printf "################################################################### \n" >> $output
printf "Showing OS files for Multiple Evidence tasks \n" >> $output
printf "/etc/passwd, /etc/groups, /etc/sudoers, /etc/sudoers.d.* FOR: \n" >> $output
printf "Evidence Task: Remove/Disable Unecessary Accounts \n" >> $output
printf "Evidence Task: Show sudo permissons for all users which have sudo enabled \n" >> $output
printf "Commands: change -i user. where user is sudo user \n" >> $output
printf "Evidence Task: Admin Password Request \n" >> $output
printf "Evidence Task: Access Needs for Each Role \n" >> $output
printf "Evidence Task: Privileges Based on Job Function \n" >> $output
printf "Evidence Task: User IDss and Documented Approvals \n" >> $output
printf "Evidence Task: User IDs and Privileges \n" >> $output
printf "Evidence Task: Access for Terminated Users \n" >> $output
printf "Evidence Task: User ID Lists \n" >> $output
printf "Evidence Task: Authentication Mechanism Only for Intended Accounts \n" >> $output
printf "Commands: cat /etc/passwd; cat /etc/groups;cat /etc/sudoers; cat /etc/sudoers.d/* \n" >> $output
show_osfiles
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: Deploy Anti-virus Software \n" >> $output
printf "Evidence Task: Actively Run Anti-Virus \n" >> $output
printf "Evidence Task:: Last password change date of all sudo users. ATTENTION: Does NOT show if user can login by sshkey only such as sftp \n" >> $output
printf "Evidence Task: Show sudo permissons for all users which have sudo enabled \n" >> $output
printf "Commands: rpm -qa falcon-sensor, ps -eaf |grep falcon-sensor \n" >> $output
printf "\n" >> $output
printf "OUTPUT: rpm -qa falcon-sensor \n" >> $output 
rpm -qa falcon-sensor >> $output 2>&1
printf "\n" >> $output
printf "OUTPUT: ps -eaf |grep falcon-sensor \n" >> $output 
ps -eaf |grep falcon-sensor >> $output 2>&1
printf "\n"
printf "OUTPUT: sudo users last passwd change. Does NOT account for ssh by key only users \n" >> $output 
user_sudo_perms

printf "################################## \n" >> $output
printf "################################## \n" >> $output

printf "Evidence Task: Default Passwords Changed \n" >> $output
printf "Commands: show only cyberark access by grep -i AllowUsers /etc/ssh/sshd_config. This is NOT a PCI Requirement \n" >> $output
printf "Commands: show build date (as best possible) by sudo rpm -qa --last|awk '{$1=""}1'|tail -1 \n" >> $output
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: Remote-login Commands \n" >> $output
printf "Unreadable Passwords During Transmission \n" >> $output
printf "Non-consumer Passwords Unreadable During Storage \n" >> $output
printf "Non-consumer Passwords Unreadable During Transmission  \n" >> $output
printf "Commands: rpm -q xinetd. No ssh or telnet-server installed leaving only ssh \n" >> $output
printf "Commands: rpm -q telnet-server. No ssh or telnet-server installed leav only ssh \n" >> $output
printf "Commands: grep -o '^[^#]*' /etc/ssh/sshd_config  \n" >> $output
printf "\n" >> $output
printf "OUTPUT: rpm -q xinetd \n" >> $output 
rpm -q xinetd >> $output 2>&1
printf "OUTPUT: rpm -q telnet-server \n" >> $output 
rpm -q telnet-server  >> $output
printf "\n\n" >> $output 2>&1
printf "FILE: /etc/ssh/sshd_config. Empty lines and comments removed grep -o '^[^#]*' \n" >> $output
grep -o '^[^#]*' /etc/ssh/sshd_config >> $output
printf "\n" >> $output 2>&1
printf "OUTPUT: rpm -q telnet-server \n" >> $output 
rpm -q telnet-server  >> $output
printf "\n\n" >> $output 2>&1
#printf "OUTPUT:  grep -o '^[^#]*' /etc/ssh/sshd_config \n" >> $output 
#printf "\n" >> $output 2>&1


cat /dev/null > /tmp/pci-report.tmp

if  ! grep -q ^AllowUsers $sshconfigfile  ; then
   printf "/etc/ssh/sshd_config AllowUsers only from specific host not set \n" >> $output
   printf "This is NOT a PCI requirement \n"  >> $output
else
   for users in `grep -i AllowUsers $sshconfigfile |sed 's/[^ ]* //'`
   do
      listuser=`echo $users |awk -F"@" '{print $1}'` 
      printf "$listuser \n" >> /tmp/pci-report.tmp
   done
   for user in `cat /tmp/pci-report.tmp|sort|uniq`
   do
      printf "$user \t" >> $output
      printf "OUTPUT:  chage -l $user |grep 'Last password change'  \n" >> $output 
      chage -l $user |grep "Last password change" >> $output 2>&1
      printf "\n" >> $output
   done
fi
printf "Evidence Task: Build Date Approximation: " >> $output
printf "OUTPUT:  rpm -qa --last  \n" >> $output 
rpm -qa --last|awk '{$1=""}1'|tail -1 >> $output 2>&1
printf "\n" >> $output
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: One Primary Function Per Server \n" >> $output
printf "Evidence Task: Remote-login Commands \n" >> $output
printf "Encrypt Non-console Administrative Access \n" >> $output
printf "Implement Strong Crytopgraphy \n" >> $output
printf "Commands: systemctl list-unit-files | grep enabled OR chkconfig --list |grep on \n" >> $output
printf "Commands: netstat -anpe|grep LISTENING \n" >> $output
printf "Commands: rpm -qa |egrep -i \"xinetd|telnet-server\" Not installed leaving only ssh \n" >> $output
printf "Commands: grep ^Protocol /etc/ssh/sshd_config \n" >> $output
if command -v systemctl &> /dev/null
then
   printf "OUTPUT:  systemctl list-unit-files \n" >> $output 
   systemctl list-unit-files | grep enabled >> $output 2>&1
   printf "\n" >> $output
else
   printf "OUTPUT: chkconfig --list |grep on \n" >> $output 
   chkconfig --list |grep on >> $output 2>&1
   printf "\n" >> $output
fi
printf "OUTPUT: netstat -anpe|grep LISTENING \n" >> $output 
netstat -anpe|grep LISTENING >> $output 2>&1
printf "\n" >> $output
printf "OUTPUT: rpm -qa |egrep -i \"xinetd|telnet-server\" \n" >> $output 
rpm -qa |egrep -i "xinetd|telnet-server" >> $output 2>&1
printf "\n" >> $output
printf "OUTPUT: ssh Protocol Version" >> $output
grep ^Protocol /etc/ssh/sshd_config >> $output 2>&1
printf "\n" >> $output
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: Critical Systems Have Correct Time \n" >> $output
printf "Commands: ntpq -p or chronyc sources \n" >> $output
printf "OUTPUT: ntpq -p or chronyc sources \n" >> $output
if command -v ntpq &> /dev/null ; then
    ntpq -p >> $output 2>&1
elif command -v chronyc &> /dev/null ; then
    chronyc sources >> $output 2>&1
else
    printf "ntp or chronyc not running \n"  >> $output
fi
printf "\n" >> $output
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: Timeframe for Vendor supplied Security Patches \n" >> $output
printf "Commands:  cat /etc/redhat-release \n" >> $output
printf "Commands: ls -l /var/log/yum.log* /var/log/up2date* \n" >> $output
printf "Commands: rpm -qa --last | awk 'NR==1 {x=$3$4$5} x==$3$4$5' |tail -1 \n" >> $output
# [ -s /tmp/f1 ] rpm -E %{rhel}
#rpm -qa --last | awk 'NR==1 {x=$3$4$5} x==$3$4$5'
printf "OUTPUT: OS Release \n" >> $output
cat /etc/redhat-release >> $output 2>&1
printf "\n" >> $output
printf "OUTPUT: Last Kernel Update \n" >> $output
rpm -qa kernel --last|head -1 >> $output 2>&1
printf "\n" >> $output
printf "OUTPUT: Last Installed or Patched \n" >> $output
rpm -qa --last | awk 'NR==1 {x=$3$4$5} x==$3$4$5' |tail -1 >> $output 2>&1
printf "\n" >> $output
printf "################################## \n" >> $output
printf "################################## \n" >> $output
printf "Evidence Task: User Password Requirements \n" >> $output
printf "Commands: cat  /etc/login.defs| grep -v '^\s*$\|^\s*\#' \n" >> $output
printf "OUTPUT: User Password Requirements via /etc/login.defs | grep -v '^\s*$\|^\s*\#' \n" >> $output
cat  /etc/login.defs| grep -v '^\s*$\|^\s*\#' >> $output 2>&1
printf "\n" >> $output
            

# Entire files already provided  above
#for file in /etc/sudoers
#do
#   for user in `cat $file |grep -v '^[[:space:]]*$' |egrep -v ^"#|^%|^ALL|^Defaults" |awk '{print $1}'`
#   do
#      printf "OUTPUT: sudo permissions for $user \n" >> $output
#      sudo -lU $user |sed -ne '/User/,$ p' >> $output
#   done
#done
#for file in `ls /etc/sudoers.d/*`
#do
#   for user in `cat $file |grep -v '^[[:space:]]*$' |egrep -v ^"#|^%|^ALL|^Defaults" |awk '{print $1}'`
#   do
#      printf "OUTPUT: sudo permissions for $user \n" >> $output
#      sudo -lU $user |sed -ne '/User/,$ p' >> $output
#      printf "\n" >> $output
#   done
#done
