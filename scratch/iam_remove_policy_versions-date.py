# iam delete policy versions
# delete only the customer managed policies versions not AWS policy versions (Scope = 'Local')
# debug output to be removed
# robinsonp 10/29/2021
#
import boto3
import datetime
import time
from time import mktime
from datetime import datetime, timedelta

iam_ob = boto3.client("iam")
time_now = datetime.now()
date_now = datetime.now()
days_to_delete = 45
last_used_date = datetime.now()
print(f"DateNow {date_now}")

response = iam_ob.list_policies(
    Scope = 'Local'
)

for iam_policy in response['Policies']:
    response = iam_ob.list_policy_versions(
        PolicyArn=(iam_policy['Arn'])
    )
    for policy_ver in response['Versions']:
        if policy_ver['IsDefaultVersion'] is True:
             pass
        else:
             policy_create_date = (policy_ver['CreateDate'])
             formatted_policy_create_date = policy_create_date.replace(tzinfo=None)
             delta_time = date_now - formatted_policy_create_date
             formatted_delta_time = delta_time.days
#             print(f"DateNow {date_now} CreateDate {formatted_policy_create_date} {policy_ver['VersionId']} {iam_policy['Arn']}")

#             if formatted_delta_time >= days_to_delete:
#                 print(f"DEFAULT YES: YES deleting {policy_ver['VersionId']} DaysOld: [ {formatted_delta_time} ] {iam_policy['Arn']}")
#             else:
#                 print(f"DEFAULT YES: NOT deleting {policy_ver['VersionId']} DaysOld: [ {formatted_delta_time} ] {iam_policy['Arn']}")
#             if delta_time.days >= days_to_delete:
#                 print(f"DEFAULT NO: YES deleting {policy_ver['VersionId']} DaysOld: [ {formatted_delta_time} ] {iam_policy['Arn']}")
#             else:
#                 print(f"DEFAULT NO: NOT deleting {policy_ver['VersionId']} DaysOld: [ {formatted_delta_time} ] {iam_policy['Arn']}")
##           delete = iam_ob.delete_policy_version(
##                   PolicyArn=(iam_policy['Arn']),
##                   VersionId=policy_ver['VersionId']
##                   )
##           print(delete)
~
