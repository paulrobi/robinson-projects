#!/bin/sh
emaillist="paul.robinson@dowjones.com"
output=/tmp/$$.checkemptydir.txt

mail_header ()
{
   cat /dev/null > $output
   printf "From: root@`uname -n` \n" >> $output
   printf "Subject: DAQ Empty Dir Check \n" >> $output
   printf "To: $emaillist \n" >> $output
   printf "\n" >> $output
}

mail_send()
{
 /usr/lib/sendmail ${emaillist} < $output
}

runcheck()
{
   printf "################ FTP DIRECTORIES #################### \n" >> $output
   for ftpdir in `cat /etc/passwd |grep FTP|egrep -v "SFTP|^ftp|^daqdataops|homedir|/var/ftp/\#|FTP User"|awk -F":" '{print $6}'`
   do
     unset emptydirs
     emptydirs=`find $ftpdir -mindepth 1 -depth -type d ! -path homedir ! -path "*.dev*" ! -path "*.ignore*" -empty`
     if [[ ! -z "$emptydirs" ]] ; then
        emptydirfound=true
        printf "$emptydirs \n"
        for dirtodelete in "$emptydirs"
        do
           printf "$dirtodelete \n" >> $output
          # rmdir -v "$dirtodelete" >> $output
        done
     fi
   done

   printf "################ SFTP DIRECTORIES #################### \n" >> $output
   for sftpdir in `cat /opt/DJ/etc/sshd2112_config |grep ChrootDirectory |awk '{print $2}' |grep -vw "/var/ftp/"`
   do
     unset emptydirs
     emptydirs=`find $sftpdir/homedir -mindepth 1 -depth -type d ! -path homedir ! -path "*.dev*" ! -path "*.ignore*" -empty`
     if [[ ! -z "$emptydirs" ]] ; then
        emptydirfound=true
        printf "$emptydirs \n"
        for dirtodelete in "$emptydirs"
        do
           printf "$dirtodelete \n" >> $output
           # rmdir -v "$dirtodelete" >> $output
        done
     fi
   done
}
######### main #############

mail_header
runcheck

if [ "$emptydirfound" == "true" ] ; then
   mail_send
else
   /bin/rm $output
fi
