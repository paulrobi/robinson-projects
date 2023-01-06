#!/bin/sh
#10/23/2020 sftp logging

s3bucket="virdjifprintsftpcf-dev"

pull_templates()
{
   if [ ! -d /home/control/build ] ; then
	   mkdir -p /home/control/build
   fi
   cd /home/control/build/
   aws s3 cp s3://${s3bucket}/build/passwd.gpg /home/control/build/passwd.gpg
   aws s3 cp s3://${s3bucket}/build/group.gpg /home/control/build/group.gpg

   cat /etc/ppfile | gpg --passphrase-fd 0 --batch --yes /home/control/build/passwd.gpg
   cat /etc/ppfile | gpg --passphrase-fd 0 --batch --yes /home/control/build/group.gpg
}

create_dirandfiles()
{
  cd /home/control/build/

  while IFS= read -r pwline
  do
    pwline=`echo $pwline |grep -i "print-sftp-user"|grep -v "print=sftp-master"`
    if [ ! -z "$pwline" ] ; then
        username=$(echo $pwline |cut -f1 -d":");
        userdisableflag=$(echo $pwline |cut -f2 -d":");
        userid=$(echo $pwline |cut -f3 -d":");
        groupid=$(echo $pwline |cut -f4 -d":");
        fullname=$(echo $pwline |cut -f5 -d":");
        homedir=$(echo $pwline |cut -f6 -d":");
        shell=$(echo $pwline |cut -f7 -d":");
        useradd --uid $userid --gid 10000 --home-dir $homedir --comment "print-sftp-user" --shell /sbin/nologin
   fi
  done < /home/control/build/passwd
  cp -p /etc/group /etc/group-bkup
  cp -p /home/control/build/group /etc/group
  chmod 644 /etc/group 
}
############################################
Date=`date '+%d%m%Y-%H%M%S'`
pull_templates
create_dirandfiles
