# iam delete policy versions
# delete only the customer managed policies versions older then $days_to_delete not AWS policy versions (Scope = 'Local')
# debug output to be removed
# robinsonp 11/1/2021
#
import boto3
import datetime
import time
from time import mktime
from datetime import datetime, timedelta

iam_ob = boto3.client("iam")
date_now = datetime.now()
days_to_delete = 45

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
             if delta_time.days >= days_to_delete:
                 print(f"DEFAULT={policy_ver['IsDefaultVersion']}  DELETING=True {policy_ver['VersionId']} DaysOld: [ {delta_time.days} ] {iam_policy['Arn']}")
#           delete = iam_ob.delete_policy_version(
#                   PolicyArn=(iam_policy['Arn']),
#                   VersionId=policy_ver['VersionId']
#                   )
#           print(delete)

             else:
                 print(f"DEFAULT={policy_ver['IsDefaultVersion']}  DELETING=False {policy_ver['VersionId']} DaysOld: [ {delta_time.days} ] {iam_policy['Arn']}")
