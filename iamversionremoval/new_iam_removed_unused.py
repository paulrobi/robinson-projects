# Read CSV for acount and Role info
# assume role for rach account
#list roles in each account unused within X days
#for Xdays roles to delete detach policies
#Delete Role in requested
#List Policies not accessed
#Delete Policies




import boto3, botocore
import subprocess, os, sys, argparse, datetime, time, csv
from time import mktime
from datetime import datetime, timedelta
boto_sts=boto3.client('sts')
client = boto3.client("iam")
date_format_str = "%Y%m%d-%H%M%S"

date_now = datetime.now()
days_to_delete = 30
default_policy_age_min = 30
max_days_since_used = 30
dest_acctnumber="186630241196"
dest_role_name="nct_cse_prod_tools_role"
#arn:aws:iam::186630241196:role/nct_cse_prod_tools_role


def perform_assume_role(account_info):
    stsresponse = boto_sts.assume_role(
      RoleArn=("arn:aws:iam::{}:role/{}".format(dest_acctnumber,dest_role_name)),
         RoleSessionName='iam_pol_ver_session',
         ExternalId='terraform_agent_request',
         DurationSeconds=900
     )
    newsession_id = stsresponse["Credentials"]["AccessKeyId"]
    newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
    newsession_token = stsresponse["Credentials"]["SessionToken"]
    return (newsession_id,newsession_key,newsession_token)

session_id,session_key,session_token = perform_assume_role([('dest_acctnumber',dest_acctnumber),('dest_role_name',dest_role_name)])
print(f'\n Session ID Main {session_id}')
print(f'\n Session Key Main {session_key}')
print(f'\n Session Token Main {session_token}')
print('\n\n##########################################')

def perform_list_roles(session_id,session_key,session_token):
    iam_assumed_client = boto3.client(
        'iam',
         aws_access_key_id=session_id,
         aws_secret_access_key=session_key,
         aws_session_token=session_token
      )
    rolesResponse = iam_assumed_client.list_roles(MaxItems=1000)
    for r in [r for r in rolesResponse['Roles'] if '/aws-service-role/' not in r['Path'] and '/service-role/' not in r['Path']]:
        jobId = client.generate_service_last_accessed_details(Arn=r['Arn'])['JobId']
        rolename=r['RoleName']
        print(f'rolename = {rolename}')
        roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
        jobAttempt = 0
        print()
        while roleAccessDetails['JobStatus'] == 'IN_PROGRESS':
            time.sleep(jobAttempt*2)
            jobAttempt = jobAttempt + 1
            roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
        if roleAccessDetails['JobStatus'] == 'FAILED':
            print(f'Unable to retrive last access report for role {0}. No action taken.\n')
        else:
            lastAccessedDates = [a['LastAuthenticated'] for a in roleAccessDetails['ServicesLastAccessed'] if 'LastAuthenticated' in a]
            myarn=r['Arn']
            print(f'{myarn} LastAccess={lastAccessedDates}')
            # not accessed in 400days
            if not lastAccessedDates:
                #report += 'Role {0} has no access history. No action taken.\n'.format( r['Arn'])
                print(f'{myarn} has no access history in 400days --delete.')
                attached_policies_response = client.list_attached_role_policies(RoleName=rolename)['AttachedPolicies']
                for attached_policies in attached_policies_response:
                    attached_policy_name=attached_policies['PolicyName']
                    attached_policy_arn=attached_policies['PolicyArn']
                    print(f'RoleName={rolename}')
                    print(f'PolicyName={attached_policy_name}')
                    print(f'PolicyArn={attached_policy_arn}')
            else:
               roleLastUsed = min(lastAccessedDates)
               daysSinceUsed = (today - roleLastUsed.replace(tzinfo=None)).days
               ### add Logic for math to delete if not accessed in X days
               if daysSinceUsed >= MaxdaysSinceUsed:
                    print(f'{myarn} days since used = {daysSinceUsed} greater then {MaxdaysSinceUsed} --delete')
                    attached_policies_response = client.list_attached_role_policies(RoleName=rolename)['AttachedPolicies']
                    for attached_policies in attached_policies_response:
                        attached_policy_name=attached_policies['PolicyName']
                        attached_policy_arn=attached_policies['PolicyArn']
                        print(f'RoleName={rolename}')
                        print(f'PolicyName={attached_policy_name}')
                        print(f'PolicyArn={attached_policy_arn}')
                        #attached_policy_detach = client.detach_role_policy(RoleName='test-role-delete-1',PolicyArn='arn:aws:iam::186630241196:role/test-role-delete-1')

               else:
                     print(f'{myarn} days since used = {daysSinceUsed} less then {MaxdaysSinceUsed} --skip')
               continue
perform_list_roles(session_id,session_key,session_token)
