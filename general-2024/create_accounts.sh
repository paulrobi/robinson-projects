#!/bin/bash
FILE="/home/list2.txt"
while IFS=":" read -r account_name home_directory _; do
if [ -n "$account_name" ]; then
   useradd -m -d "$home_directory" -s /bin/bash "$account_name"
   chmod 755 "$home_directory"
   chown "$account_name":"$account_name" "$home_directory"
   echo "User account $account_name created with home directory $home_directory"
fi
done < "$FILE"


FILE="/home/list2.txt"
CPPGMDRI:/var/ftp/GMDRI:CPPGMDRI:ftp
CPPGMDRI1:/var/ftp/GMDRI1:CPPGMDRI1:ftp
CPPNEOSTG1:/var/ftp/NEOSTG:CPPNEOSTG1:ftp
CPPSHINS:/var/ftp/SHINS:CPPSHINS:ftp
CPPSOCITA:/var/ftp/SOCITA:CPPSOCITA:ftp


FILE="/home/list.txt"
CPPGMDRI:/var/ftp/GMDRI/GMDRI:CPPGMDRI:ftp
CPPGMDRI1:/var/ftp/GMDRI1/GMDRI1:CPPGMDRI1:ftp
CPPNEOSTG1:/var/ftp/NEOSTG/NEOSTG:CPPNEOSTG1:ftp
CPPSHINS:/var/ftp/SHINS/ON:CPPSHINS:ftp
CPPSHINS:/var/ftp/SHINS/SN:CPPSHINS:ftp
CPPSOCITA:/var/ftp/SOCITA/temp.ignore:CPPSOCITA:ftp


#!/bin/bash
FILE="/home/list.txt"
while IFS=":" read -r account_owner create_directory _; do
if [ -n "$account_owner" ]; then
   mkdir "$create_directory"
    chown "$account_owner":ftp "$create_directory"
    chmod 775 "$create_directory"
   echo "subdirectory for $account_owner created $create_directory"
fi
done < "$FILE"
