#!/bin/sh
s3virbucket="virdjifprintsftpcf-dev"
s3orebucket="oredjifprintsftpcf-dev"
#seconds since last modification (3600 = 1hr)
lastmodsecmax=3600
files2sync="/etc/passwd /etc/shadow /etc/group"
export PATH=$PATH:/usr/local/bin

oldtime=$polling
curtime=$(date +%s)
HOST=`uname -n`

do_s3sync()
{
  printf "do_s3sync entered $curtime \n"
   mkdir -p /home/control/sync_os_files
   cd /home/control/sync_os_files
   cat /etc/ppfile | gpg -c  --passphrase-fd 0 --batch --yes --output /home/control/sync_os_files/passwd.gpg /etc/passwd
   cat /etc/ppfile | gpg -c  --passphrase-fd 0 --batch --yes --output /home/control/sync_os_files/shadow.gpg /etc/shadow
   cat /etc/ppfile | gpg -c  --passphrase-fd 0 --batch --yes --output /home/control/sync_os_files/group.gpg /etc/group

   /usr/local/bin/aws s3 cp  /home/control/sync_os_files/passwd.gpg s3://${s3virbucket}/build/
   /usr/local/bin/aws s3 cp  /home/control/sync_os_files/shadow.gpg s3://${s3virbucket}/build/
   /usr/local/bin/aws s3 cp  /home/control/sync_os_files/group.gpg s3://${s3virbucket}/build/
   /usr/local/bin/aws s3 sync s3://$s3virbucket s3://$s3orebucket
}

   sync2s3=no
   for file in $files2sync
   do
      filetime=$(/bin/stat $file -c %Y)
      timediff=$(expr $curtime - $filetime)
      if (( timediff <= lastmodsecmax )); then
         printf "$file updated within last $lastmodsecmax seconds \n"
         sync2s3=yes
      fi
   done

   if [[ $sync2s3 = yes ]] ; then
      do_s3sync
   else
      printf "no updates in past $lastmodsecmax seconds\n"
   fi
