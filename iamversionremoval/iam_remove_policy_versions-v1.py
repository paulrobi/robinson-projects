# iam delete policy versions
# delete only the customer managed policies versions not AWS policy versions (Scope = 'Local')
# requires python3 boto3 iam permissions {"iam:ListPolicies","iam:GetPolicyVersion",iam:ListPolicyVersions",iam:CreatePolicyVersion",iam:DeletePolicyVersion"}
# debug output to be removed
# robinsonp 10/29/2021
#
import boto3
iam_ob = boto3.client("iam")

response = iam_ob.list_policies(
    Scope = 'Local'
)

for iam_policy in response['Policies']:
    response = iam_ob.list_policy_versions(
        PolicyArn=(iam_policy['Arn'])
    )
    for policy_ver in response['Versions']:
        if policy_ver['IsDefaultVersion'] is True:
            print(f"OnlyDefault {policy_ver['VersionId']} {iam_policy['Arn']}")
#           pass
        else:
           print(f"Deleting {policy_ver['VersionId']}: {iam_policy['Arn']} Version")
           delete = iam_ob.delete_policy_version(
                   PolicyArn=(iam_policy['Arn']),
                   VersionId=policy_ver['VersionId']
                   )
           print(delete)
