#!/bin/python

import os
import sys


def iamlistversions(iamarn):
  var = raw_input('arn:aws:iam::510639184942:policy/robinson-test-policy-versions')
#  print "test, var"
  #os.system("aws iam list-policy-versions --query "Versions[?@.IsDefaultVersion == \`false\`].VersionId" --policy-arn %s --output text", %(var))
  os.system("aws iam list-policy-versions --query 'Versions[?@.IsDefaultVersion == \`false\`].VersionId' --policy-arn %s --output text", %(var))

  #aws iam list-policy-versions --query "Versions[?@.IsDefaultVersion == \`false\`].VersionId" --policy-arn iamarn --output text

#function iam-delete-policy-versions () {
#  iam-list-versions $1 | xargs -n 1 -I{} aws iam delete-policy-version --policy-arn $1 --version-id {}
#}


iamlistversions ("arn:aws:iam::510639184942:policy/robinson-test-policy-versions")
os.system("date")
[root@ip-10-161-233-146 bin]# cat t1.sh
#!/bin/bash
RAW_POLICIES=$(aws iam list-policies --scope Local --query Policies[].[Arn,PolicyName,DefaultVersionId])
POLICIES=$(echo $RAW_POLICIES | tr -d " " | sed 's/\],/\]\n/g')
for POLICY in $POLICIES
    do echo $POLICY | cut -d '"' -f 4
    echo -e "---------------\n"
#    aws iam get-policy-version --version-id $(echo $POLICY | cut -d '"' -f 6) --policy-arn $(echo $POLICY | cut -d '"' -f 2)
#    echo -e "\n-----------------\n"
done
