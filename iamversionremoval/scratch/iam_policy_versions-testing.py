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

arn:aws:iam::510639184942:policy/robinson-test-policy-versions
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.get_policy_version
