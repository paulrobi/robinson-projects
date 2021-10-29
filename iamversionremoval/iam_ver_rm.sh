#!/bin/bash
policy="arn:aws:iam::510639184942:policy/robinson-test-policy-versions"

function iam-list-versions () {
  aws iam list-policy-versions --query "Versions[?@.IsDefaultVersion == \`false\`].VersionId" --policy-arn $1 --output text
}

function iam-delete-policy-versions () {
  iam-list-versions $1 | xargs -n 1 -I{} aws iam delete-policy-version --policy-arn $1 --version-id {}
}

iam-delete-policy-versions "$policy"

#versions=$(iam-list-versions $policy)
#printf "$versions\n"
#for version_to_delete in $versions
#do
#  aws iam delete-policy-version --policy-arn $policy --version-id $version_to_delete
#done


###for policy in `aws iam list-policies --scope Local | jq -r '.Policies[] |select(.PolicyName)| .Arn'`
###do
#  policy="arn:aws:iam::510639184942:policy/robinson-test-policy-versions"
#  unset versions
#  versions=$(aws iam list-policy-versions --query "Versions[?@.IsDefaultVersion == \`false\`].VersionId" --policy-arn $policy --output text)
#  if [ ! -z "$versions" ] ; then
#     printf "$policy $versions \n"
#  fi
#  for oldversion in $versions
#  do
#
###done
#  printf "$versions \n"
