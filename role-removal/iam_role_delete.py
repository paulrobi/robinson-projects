import boto3, botocore
import subprocess, os, sys, argparse, datetime, time, csv
from time import mktime
from csv import reader
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
dest_assume_role_name="nct_cse_prod_tools_role"
#arn:aws:iam::186630241196:role/nct_cse_prod_tools_role

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv_input', default='18JAN2022-mytest-roles.csv')
args = parser.parse_args()

if os.path.isfile(args.csv_input):
   pass
else:
   sys.exit(f'Inputfile {args.csv_input} does not exist')

# create output csv
outputfile = open('iam_rm_role_policies_output.csv', 'w',newline='')
csv_write = csv.writer(outputfile,delimiter=',')
output_header = "AccountId,AccountName,AccountEnv,DryRun(Y|N),AssumeRoleStatus,Name,Type(Role|Policy),Action,Age,LastUsed\n"
outputfile.write(output_header)

# assume role for account function
def perform_assume_role(account_info):
    stsresponse = boto_sts.assume_role(
      RoleArn=("arn:aws:iam::{}:role/{}".format(dest_acctnumber,dest_assume_role_name)),
         RoleSessionName='iam_pol_ver_session',
         ExternalId='terraform_agent_request',
         DurationSeconds=900
     )
    ###x print(stsresponse["Credentials"]["AccessKeyId"])
    return (stsresponse["Credentials"]["AccessKeyId"],stsresponse["Credentials"]["SecretAccessKey"],stsresponse["Credentials"]["SessionToken"])

def perform_remove_role_from_instance_profile(rolename):
    print(f'Entered>>> perform_remove_role_from_instance_profile {rolename}')
    inst_profile = client.list_instance_profiles_for_role(RoleName=rolename)
    for inst_profile in inst_profile['InstanceProfiles']:
        pass
        ###x print(f'Status Role {rolename} Removed from InstanceProfile {inst_profile}')
        ###x res2 = client.remove_role_from_instance_profile( RoleName=rolename, InstanceProfileName=inst_profile['InstanceProfileName'])

def perform_remove_instance_profile(rolename):
    print("****************************")
    paginator = client.get_paginator('list_instance_profiles_for_role')
    for response in paginator.paginate(RoleName=rolename):
        for instanceProfile in response['InstanceProfiles']:
            pass
            ###x print(f'Status InstanceProfileToRemoved {instanceProfile}')
            ###x client.remove_role_from_instance_profile(
            ###x         RoleName=rolename,
            ###x         InstanceProfileName=instanceProfile['InstanceProfileName']
            ###x )
    print("****************************")


def perform_policy_detach(rolename):
    print(f'Entered>>> perform_policy_detach {rolename}')
    attached_policies_response = client.list_attached_role_policies(RoleName=rolename)['AttachedPolicies']
    for attached_policy in attached_policies_response:
        attached_policy_name = attached_policy['PolicyName']
        attached_policy_arn = attached_policy['PolicyArn']
        ###X print(f'RoleName={rolename} PolicyName={attached_policy_name} PolicyArn={attached_policy_arn}')
        print(f'RoleName={rolename} PolicyName={attached_policy_name}')
        ###X print(f'Status AttachedPolicyDetached = {attached_policy}')
        ###x attached_policy_detach = client.detach_role_policy(RoleName=rolename,PolicyArn=attached_policy_arn)
    attached_inline_policies_response = client.list_role_policies(RoleName=rolename)['PolicyNames']
    for attached_inline_policy in attached_inline_policies_response:
        print(f'RoleName={rolename} InlinePolicyName = {attached_inline_policy}')
        ###x print(f'Status AttachedInlinePolicyDetached = {attached_inline_policy}')
        ###x client.delete_role_policy(RoleName=rolename,PolicyName=attached_inline_policy)


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
                ###x client.delete_role(RoleName=rolename)
            else:
               rolelastused = min(last_accessed_date)
               days_since_used = (date_now - rolelastused.replace(tzinfo=None)).days
               ### add Logic for math to delete if not accessed in X days
               if days_since_used >= maxdays_since_used:
                    print(f'{myarn} days since used = {days_since_used} greater then {maxdays_since_used} --delete')
                    perform_policy_detach(rolename)
                    perform_remove_role_from_instance_profile(rolename)
                    perform_remove_instance_profile(rolename)
                    ###x client.delete_role(RoleName=rolename)
               else:
                     action_taken ="Skip-Role-Deletion:"
                     print(f'{myarn} days since used = {days_since_used} less then {maxdays_since_used} --skip')
               continue

# MAIN
# perform read of input csv
with open(args.csv_input, 'r') as csv_file_input:
     csv_reader = csv.DictReader(csv_file_input)
     for line in csv_reader:
         newsession_token = "None"
         policy_name = "AssumeRoleError"
         policy_isdefault = "AssumeRoleError"
         formatted_policy_create_date = "AssumeRoleError"
         dest_account_id = line['cloud_provider_id']
         dest_account_name = line['account_name']
         dest_role_name = line['asset_name']

         with open('aws_account_assumed_roles.csv', 'r') as csv_acct_file_input:
             csv_acct_reader = csv.DictReader(csv_acct_file_input)
             for acct_file_line in csv_acct_reader:
                 if acct_file_line['accountnumber'] == line['cloud_provider_id']:
                    ###x print(f'dest_account_id::{dest_account_id} dest_account_name::{dest_account_name} dest_role_name::{dest_role_name}')
                    session_id,session_key,session_token = perform_assume_role([('dest_acctnumber',dest_acctnumber),('dest_assume_role_name',dest_assume_role_name)])
                    iam_assumed_client = boto3.client('iam', aws_access_key_id=session_id, aws_secret_access_key=session_key, aws_session_token=session_token)
                    print('\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    perform_role_maintenance(session_id,session_key,session_token)
