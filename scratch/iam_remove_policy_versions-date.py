# iam delete policy versions
# delete only the customer managed policies versions older then $days_to_delete not AWS policy versions (Scope = 'Local')
# debug output to be removed
# robinsonp 11/7/2021
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
days_to_delete = 30

boto_sts=boto3.client('sts')

action = "debug"
dryrun = "True"

outputfile = open('output-iam_policy_versions-outout.csv', 'w')
output_header = "AccountId,AccountName,PolicyName,IsDefaultVersion,PolicyAge,PolicyCreateDate,ProfileVersion,Action,DryRun,AssumedRoleError\n"
outputfile.write(output_header)

with open('iam_policy_versions-template.csv', 'r') as csv_file_input:
     csv_reader = csv.DictReader(csv_file_input)

     for line in csv_reader:
         dest_account_id = line['AccountId']
         dest_role_name = line['DestRoleName']
         dest_account_name = line['AccountName']
         try:
            stsresponse = boto_sts.assume_role(
                RoleArn=("arn:aws:iam::{acctnumber}:role/{acctname}".format(acctnumber=dest_account_id, acctname=dest_role_name)),
                RoleSessionName='iam_pol_ver_session',
                DurationSeconds=900
             )
            newsession_id = stsresponse["Credentials"]["AccessKeyId"]
            newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
            newsession_token = stsresponse["Credentials"]["SessionToken"]
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
                policy_name=(iam_policy['PolicyName'])
                for policy_ver in response['Versions']:
                    policy_create_date = (policy_ver['CreateDate'])
                    formatted_policy_create_date = policy_create_date.replace(tzinfo=None)
                    delta_time = date_now - formatted_policy_create_date

                    if policy_ver['IsDefaultVersion'] is True:
                         policy_isdefault="True"
                    else:
                         policy_isdefault="False"
                         if delta_time.days >= days_to_delete:
                            action="delete"
                         else:
                            action="skip"
                            print("Generic Pass")

                assumerole_error = "SuccessAssumeRole"
                output_row = "{},{},{},{},{},{},{},{},{},{}\n".format(
                            dest_account_id, dest_account_name, policy_name,
                            policy_isdefault, formatted_policy_create_date, policy_ver['VersionId'],
                            delta_time,action,dryrun, assumerole_error
                 )
                outputfile.write(output_row)
         except botocore.exceptions.ClientError as e:
                assumerole_error = "ErrorAssumeRole"
                output_row = "{},{},{},{},{},{},{},{},{},{}\n".format(
                            dest_account_id, dest_account_name, policy_name,
                            policy_isdefault, formatted_policy_create_date, policy_ver['VersionId'],
                            delta_time,action,dryrun, assumerole_error
                 )
                outputfile.write(output_row)
                print("Client Error")

#file_handle.close()
#file_handle.close()
