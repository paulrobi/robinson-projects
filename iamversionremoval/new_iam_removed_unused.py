# Read CSV for acount and Role info
# assume role for each account
# -log error on role assume
# collect roles in each account unused within X days
# -log roles collected
# for Xdays roles to delete detach policies
# -log policies detached
# Delete Role in requested
# -log role deleted
# collect Policies not accessed
# -log policies not attached and deleted
# Delete Policies

# Nested dictionary having same keys
#Dict = { 'Dict1': {'name': 'Ali', 'age': '19'},
#         'Dict2': {'name': 'Bob', 'age': '25'}}
# Prints value corresponding to key 'name' in Dict1
#print(Dict['Dict1']['name'])
# InstanceProfile info pull
#https://www.programcreek.com/python/?CodeExample=list+profiles
#paginator = client.get_paginator('list_instance_profiles_for_role')
#    for response in paginator.paginate(RoleName=args.get('roleName')):
#        for instanceProfile in response['InstanceProfiles']:
#            data.append({
#                'Path': instanceProfile['Path'],
#                'InstanceProfileName': instanceProfile['InstanceProfileName'],
#                'InstanceProfileId': instanceProfile['InstanceProfileId'],
#                'CreateDate': datetime.strftime(instanceProfile['CreateDate'], '%Y-%m-%dT%H:%M:%S'),
#                'Arn': instanceProfile['Arn'],
#            })
#            output.append(instanceProfile)


import boto3, botocore
import subprocess, os, sys, argparse, datetime, time, csv
from time import mktime
from datetime import datetime, timedelta
boto_sts=boto3.client('sts')
client = boto3.client("iam")
date_format_str = "%Y%m%d-%H%M%S"

date_now = datetime.now()
maxdays_since_used = 30
days_to_delete = 30
default_policy_age_min = 30
max_days_since_used = 30
dest_acctnumber="186630241196"
dest_role_name="nct_cse_prod_tools_role"
#arn:aws:iam::186630241196:role/nct_cse_prod_tools_role

# create output csv
outputfile = open('iam_rm_role_policies_output.csv', 'w',newline='')
csv_write = csv.writer(outputfile,delimiter=',')
output_header = "AccountId,AccountName,AccountEnv,DryRun(Y|N),AssumeRoleStatus,Name,Typei(Role|Policy),Action,Age,LastUsed\n"
outputfile.write(output_header)

# assume role for account function
def perform_assume_role(account_info):
    stsresponse = boto_sts.assume_role(
      RoleArn=("arn:aws:iam::{}:role/{}".format(dest_acctnumber,dest_role_name)),
         RoleSessionName='iam_pol_ver_session',
         ExternalId='terraform_agent_request',
         DurationSeconds=900
     )
    return (stsresponse["Credentials"]["AccessKeyId"],stsresponse["Credentials"]["SecretAccessKey"],stsresponse["Credentials"]["SessionToken"])

def perform_remove_role_from_instance_profile(rolename):
    print(f'Entered>>> perform_remove_role_from_instance_profile {rolename}')
    inst_profile = client.list_instance_profiles_for_role(RoleName=rolename)
    for inst_profile in inst_profile['InstanceProfiles']:
        testxxx = inst_profile['InstanceProfileName']
        print(f'Profile Name = {testxxx}')
        res2 = client.remove_role_from_instance_profile( RoleName=rolename, InstanceProfileName=inst_profile['InstanceProfileName'])

def perform_remove_instance_profile(rolename):
    print("****************************")
    paginator = client.get_paginator('list_instance_profiles_for_role')
    for response in paginator.paginate(RoleName=rolename):
        for instanceProfile in response['InstanceProfiles']:
            profilenamex = instanceProfile['InstanceProfileName'],
            print(profilenamex)
            client.remove_role_from_instance_profile(
                    RoleName=rolename,
                    InstanceProfileName=instanceProfile['InstanceProfileName']
            )
    print("****************************")


def perform_policy_detach(rolename):
    print(f'Entered>>> perform_policy_detach {rolename}')
    attached_policies_response = client.list_attached_role_policies(RoleName=rolename)['AttachedPolicies']
    #print(attached_policies_response)
    for attached_policies in attached_policies_response:
        attached_policy_name = attached_policies['PolicyName']
        attached_policy_arn = attached_policies['PolicyArn']
        print(f'RoleName={rolename}')
        print(f'PolicyName={attached_policy_name}')
        print(f'PolicyArn={attached_policy_arn}')
        attached_policy_detach = client.detach_role_policy(RoleName=rolename,PolicyArn=attached_policy_arn)
    attached_inline_policies_response = client.list_role_policies(RoleName=rolename)['PolicyNames']
    for attached_inline_policy in attached_inline_policies_response:
        print(f'Attached Inline Policy = {attached_inline_policy}')
        client.delete_role_policy(RoleName=rolename,PolicyName=attached_inline_policy)




#list roles in selected account mark those over X days since accessed
def perform_role_maintenance(session_id,session_key,session_token):
    rolesResponse = iam_assumed_client.list_roles(MaxItems=1000)
    for r in [r for r in rolesResponse['Roles'] if 'test-role-delete' in r['RoleName'] and '/aws-service-role/' not in r['Path'] and '/service-role/' not in r['Path']]:
        jobId = client.generate_service_last_accessed_details(Arn=r['Arn'])['JobId']
        rolename=r['RoleName']
        print("###################################")
        print(f'RoleName={rolename}')
        roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
        jobAttempt = 0
        while roleAccessDetails['JobStatus'] == 'IN_PROGRESS':
            time.sleep(jobAttempt*2)
            jobAttempt = jobAttempt + 1
            roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
        if roleAccessDetails['JobStatus'] == 'FAILED':
            action_taken ="skip: unable to report"
            print(f'Unable to retrive last access report for role {0}. No action taken.\n')
        else:
            last_accessed_date = [a['LastAuthenticated'] for a in roleAccessDetails['ServicesLastAccessed'] if 'LastAuthenticated' in a]
            myarn=r['Arn']
            # not accessed in 400days
            if not last_accessed_date:
                last_accessed_date = "NoAccess in over 400days"
                action_taken ="Delete-Role: "
                print(f'Action={action_taken} {rolename}')
                print(f'{myarn} LastAccess={last_accessed_date}')
                perform_policy_detach(rolename)
                perform_remove_role_from_instance_profile(rolename)
                perform_remove_instance_profile(rolename)
                client.delete_role(RoleName=rolename)
            else:
               rolelastused = min(last_accessed_date)
               days_since_used = (date_now - rolelastused.replace(tzinfo=None)).days
               ### add Logic for math to delete if not accessed in X days
               if days_since_used >= maxdays_since_used:
                    print(f'{myarn} days since used = {days_since_used} greater then {maxdays_since_used} --delete')
                    perform_policy_detach(rolename)
                    perform_remove_role_from_instance_profile(rolename)
                    perform_remove_instance_profile(rolename)
                    client.delete_role(RoleName=rolename)
               else:
                     action_taken ="Skip-Role-Deletion:"
                     print(f'{myarn} days since used = {days_since_used} less then {maxdays_since_used} --skip')
               continue

# MAIN
session_id,session_key,session_token = perform_assume_role([('dest_acctnumber',dest_acctnumber),('dest_role_name',dest_role_name)])
iam_assumed_client = boto3.client('iam', aws_access_key_id=session_id, aws_secret_access_key=session_key, aws_session_token=session_token)
print('\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
perform_role_maintenance(session_id,session_key,session_token)
