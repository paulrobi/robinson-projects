#!/bin/bash


if [ $# -ne 1 ]; then
   echo "Usage Error $0 \"\$groupid:\$yourgroupname\" ex. 877999:appxsupport "
   exit 1
fi
eapentry=$1
eapgid=`echo $eapentry|awk -F":" '{print $1}'`
eapname=`echo $eapentry|awk -F":" '{print $2}'`

printf "Add GroupID=$eapgid GroupName=eapname Y|N \n"
printf "> "
read hold
case ${hold} in
  y|Y) if ! grep  -q sudoergroup /etc/sudoers  ; then
          sed -i '/## Allows people in group wheel to run all commands[^\n]*/,$!b;//{x;//p;g};//!H;$!d;x;s//&\n%sudoergroup\tALL=(ALL)\t\tNOPASSWD: ALL\n/' /etc/sudoers
      fi

      if ! grep  -q sudoergroup /etc/group  ; then
         echo "sudoergroup:x:680006:" >> /etc/group
      fi

      if ! grep $eapentry /etc/pam.d/su ; then
         sed -i "/device_gid=600001/ s/$/|$eapentry/" /etc/pam.d/su
      fi

      if ! grep $eapentry /etc/pam.d/sudo ; then
         sed -i "/device_gid=600001/ s/$/|$eapentry/" /etc/pam.d/sudo
      fi

      if ! grep $eapentry /etc/pam.d/sshd ; then
         sed -i "/device_gid=600001/ s/$/|$eapentry/" /etc/pam.d/sshd
      fi
      if ! grep $eapentry /etc/pam.d/eap-q ; then
         sed -i "/device_gid=600001/ s/$/|$eapentry/" /etc/pam.d/eap-q
      fi
      ;;
  n|N) printf "No changes made. exiting \n"
       exit 0
     ;;
  *) printf "responce not y|n. No changes made. exiting \n"
       exit 1
     ;;
esac

