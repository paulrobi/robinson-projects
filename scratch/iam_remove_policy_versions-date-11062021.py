# iam delete policy versions
# delete only the customer managed policies versions older then $days_to_delete not AWS policy versions (Scope = 'Local')
# debug output to be removed
# robinsonp 11/6/2021
#https://www.slsmk.com/use-boto3-to-assume-a-role-in-another-aws-account/

# 186630241196,Robinson-Home,nct_cse_prod_tools_role

import boto3
import argparse
import datetime
import time
from time import mktime
from datetime import datetime, timedelta
import sys
import csv
import botocore
sts_client = boto3.client('sts')
date_format_str = "%Y%m%d-%H%M%S"

iam_ob = boto3.client("iam")
date_now = datetime.now()
days_to_delete = 45

boto_sts=boto3.client('sts')

with open('output-iam_policy_versions-outout.csv', 'w') as scriptoutput:
          fieldnames = ['AccountId','AccountName','ProfileArn','ProfileVersion','Action','LiveRun','Error']
          csv_output_writer = csv.DictWriter(scriptoutput, fieldnames=fieldnames, delimiter=',')
          csv_output_writer.writeheader()
with open('iam_policy_versions-template.csv', 'r') as csv_file_input:
     csv_reader = csv.DictReader(csv_file_input)

     for line in csv_reader:
         dest_account_id = line['AccountId']
         dest_role_name = line['DestRoleName']
         try:
            stsresponse = boto_sts.assume_role(
                RoleArn=("arn:aws:iam::{acctnumber}:role/{acctname}".format(acctnumber=dest_account_id, acctname=dest_role_name)),
                RoleSessionName='iam_pol_ver_session',
                DurationSeconds=900
             )
            newsession_id = stsresponse["Credentials"]["AccessKeyId"]
            newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
            newsession_token = stsresponse["Credentials"]["SessionToken"]
#           print ("newsession_id {}:newsession_key{}:newsession_token{}".format(newsession_id,newsession_key,newsession_token))
            iam_assumed_client = boto3.client(
                  'iam',
                  aws_access_key_id=newsession_id,
                  aws_secret_access_key=newsession_key,
                  aws_session_token=newsession_token
            )
            response = iam_assumed_client.list_policies( Scope = 'Local' )
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
####### HERE ######
###                             csv_output_writer.writerow({
###                                    'AccountId': dest_account_id,
###                                    'AccountName':
                         else:
                             print(f"DEFAULT={policy_ver['IsDefaultVersion']}  DELETING=False {policy_ver['VersionId']} DaysOld: [ {delta_time.days} ] {iam_policy['Arn']}")
         except botocore.exceptions.ClientError as e:
                  print("Client Error")


###          for line in csv_reader:
###              csv_writer.writerow(line)
