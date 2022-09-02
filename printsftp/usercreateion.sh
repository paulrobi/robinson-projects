#!/bin/bash

ec2_hostname=`uname -n`
case $ec2_hostname in
        virprintsftpctlrprod)
                printf "ec2_hostname=ec2_hostname \n"
                ;;
        oreprintsftpctlrprod)
                printf "ec2_hostname=ec2_hostname \n"
                ;;
        virprintsftpctlrstag)
                account="756005194603"
                vir_instance_region="us-east-1"
                ore_instance_region="us-west-2"
                vir_region_endpoint_url="https://secretsmanager.us-east-1.amazonaws.com"
                ore_region_endpoint_url="https://secretsmanager.us-west-2.amazonaws.com"
                vir_efs="fs-01b854d1f382ec740"
                ore_efs="fs-0fc1e2ab7d5e40f72"
                vir_s3bucket="virdjifprintsftpcf-stag"
                ore_s3bucket="oredjifprintsftpcf-stag"
                vir_transfer_server="s-21b08213af8443ca9"
                ore_transfer_server="s-ac6d7e0559ce4032a"
                environment="stag"
                scriptenv="STAGING"
                remote_host="oreprintsftpctlrstag.prtstag.dowjones.io."
                remote_sshkey="/root/.ssh/oreprintstag.priv"
                ;;
        oreprintsftpctlrstag)
                printf "Must be Executed from virprintsftpctlrstag NOT oregon oreprintsftpctlrstag \n"
                exit 1
               ;;
esac
sshoptions="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o Connecttimeout=3 -o NumberOfPasswordPrompts=1 -o LogLevel=ERROR -i $remote_sshkey"


options=$@
for i in "$@"
do
case $i in
    -add)
                adduser=yes
                shift
    ;;
    -accesstype=*)
                account_type_entered="${i#*=}"
                shift
    ;;
    -username=*)
                username_entered="${i#*=}"
                shift
    ;;
    -password=*)
                password_entered="${i#*=}"
                shift
    ;;
    -userdir=*)
                userdir_entered="${i#*=}"
                shift
    ;;
    *)
                printf "usage $0 -accesstype=(readwrite|readonly)  -username=(loginid),  -password=(unencrypted password) \n"
            exit 1
    ;;
esac
done
formatted_dir="${userdir_entered:1}"

if [[ "$account_type_entered" == "readonly" ]] ; then
        userrole="djprint-sftpclient-readonly-role"
else
        userrole="djprint-sftpclient-readwrite-role"
fi

if [[ "$adduser" == "yes" ]] ; then
   /sbin/useradd --create-home --home $userdir_entered --comment "print-sftp-user" --gid 10000 --shell /sbin/nologin --password ${password_entered}  $username_entered
   if [ $? == 0 ] ; then
        vir_user_template="/home/control/json_templates/sftp_template.json-vir_${username_entered}.json"
        /bin/cp /home/control/json_templates/sftp_template.json $vir_user_template
        secretname="$vir_transfer_server/$username_entered"
        users_uid=`/bin/id -u $username_entered`
        chown $username_entered:sftp $userdir_entered
        chmod 770 $userdir_entered
        chmod 770 /sftp/print/$username_entered
        chown $username_entered:sftp /sftp/print/$username_entered
        /bin/sed -i -e "s|CHANGE_PASSWD|$password_entered|g" $vir_user_template
        /bin/sed -i -e "s|CHANGE_ACCT|$account|g" $vir_user_template
        /bin/sed -i -e "s|CHANGE_ROLE|$userrole|g" $vir_user_template
        /bin/sed -i -e "s|CHANGE_EFS|$vir_efs|g" $vir_user_template
        /bin/sed -i -e "s|CHANGE_USERDIR|$formatted_dir|g" $vir_user_template
        /bin/sed -i -e "s|CHANGE_UID|$users_uid|g" $vir_user_template
        /usr/local/bin/aws secretsmanager create-secret --name $secretname --secret-string file://$vir_user_template
   else
        printf "`uname -n` OS User Creation Error. Contact Sys. Admin. \n"
        exit1
   fi
# Execute on Oregon
   /bin/ssh $sshoptions root@$remote_host "/sbin/useradd --create-home --home $userdir_entered --comment "print-sftp-user" --gid 10000 --shell /sbin/nologin --password ${password_entered}  $username_entered"
   if [ $? == 0 ] ; then
        ore_user_template="/home/control/json_templates/sftp_template.json-vir_${username_entered}.json"
        /bin/cp /home/control/json_templates/sftp_template.json $ore_user_template
        secretname="$ore_transfer_server/$username_entered"
        users_uid=`/bin/ssh $sshoptions root@$remote_host /bin/id -u $username_entered`
        /bin/ssh $sshoptions root@$remote_host "/bin/chown $username_entered:sftp $userdir_entered"
        /bin/ssh $sshoptions root@$remote_host "/bin/chmod 770 $userdir_entered"
        /bin/ssh $sshoptions root@$remote_host "/bin/chmod 770 /sftp/print/$username_entered"
        /bin/ssh $sshoptions root@$remote_host "/bin/chown $username_entered:sftp /sftp/print/$username_entered"
        /bin/sed -i -e "s|CHANGE_PASSWD|$password_entered|g" $ore_user_template
        /bin/sed -i -e "s|CHANGE_ACCT|$account|g" $ore_user_template
        /bin/sed -i -e "s|CHANGE_ROLE|$userrole|g" $ore_user_template
        /bin/sed -i -e "s|CHANGE_EFS|$vir_efs|g" $ore_user_template
        /bin/sed -i -e "s|CHANGE_USERDIR|$formatted_dir|g" $ore_user_template
        /bin/sed -i -e "s|CHANGE_UID|$users_uid|g" $ore_user_template
        /bin/scp $sshoptions $ore_user_template root@$remote_host:$ore_user_template
        /bin/ssh $sshoptions root@$remote_host "/usr/local/bin/aws secretsmanager create-secret --name $secretname --secret-string file://$ore_user_template"
   else
        printf "`uname -n` OS User Creation Error. Contact Sys. Admin. \n"
        exit1
   fi
fi
