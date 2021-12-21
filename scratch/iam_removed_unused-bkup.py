# updated Thu Dec 16 17:11:47 UTC 2021
import boto3, botocore
import subprocess, os, sys, argparse, datetime, time, csv
from time import mktime
from datetime import datetime, timedelta
boto_sts=boto3.client('sts')
client = boto3.client("iam")
date_format_str = "%Y%m%d-%H%M%S"

today = datetime.now()
days_to_delete = 30
default_policy_age_min = 30


action = "debug"
dryrun = "True"

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv_input', default='iam_policy_versions-accounts.csv')
parser.add_argument('-a', '--action_input', default="ReportOnly")
parser.add_argument('-e', '--env_input', default="NonProd")
args = parser.parse_args()
enviroment = args.env_input
print (args.action_input)
print (args.env_input)

if args.env_input != 'prod' and args.env_input != 'all':
   enviroment = "nonprod"
   print(f'args.env_input {args.env_input} set enviroment {enviroment}')

# Exit if no input file found
if os.path.isfile(args.csv_input):
   pass
else:
   sys.exit(f'Inputfile {args.csv_input} does not exist')


outputfile = open('iam_policy_versions-output.csv', 'w')
output_header = "AccountId,AccountName,AccountEnv,PolicyName,DryRun,AssumeRoleStatus,IsDefaultVersion,Action,ProfileVersion,PolicyAge,PolicyCreateDate\n"
outputfile.write(output_header)

def output_csvline ( AccountId,AccountName,AccountEnv,Type,
                    RolePolicyName,RoleLastUsed,PolicyInUse,Action,
                    DryRun,AssumeRoleStatus
                   ):
    output_row = f"{dest_account_id},{dest_account_name},{dest_account_env},{type},{role_policy_name},{rolelastused},{policyinuse},{action},{dryrun},{assunedrolestatus}\n"
    outputfile.write(output_row)
    return


with open(args.csv_input, 'r') as csv_file_input:
     csv_reader = csv.DictReader(csv_file_input)

     for line in csv_reader:
         newsession_token = "None"
         policy_name = "AssumeRoleError"
         policy_isdefault = "AssumeRoleError"
         formatted_policy_create_date = "AssumeRoleError"
         policy_version = "AssumeRoleError"
         policy_age = "AssumeRoleError"
         assumerole_error = "AssumeRoleError"

         dest_account_id = line['AccountId']
         dest_account_name = line['AccountName']
         dest_account_env = line['AccountEnv']
         if dest_account_env != "prod" and dest_account_env != "all":
             dest_account_env = "nonprod"
         dest_role_name = line['DestRoleName']
         print(f'enviroment = {enviroment} dest_account_env= {dest_account_env}')
         if enviroment == dest_account_env or enviroment == 'all':
            try:
               stsresponse = boto_sts.assume_role(
                   RoleArn=("arn:aws:iam::{acctnumber}:role/{acctname}".format(acctnumber=dest_account_id, acctname=dest_role_name)),
                   RoleSessionName='iam_pol_ver_session',
                   ExternalId='terraform_agent_request',
                   DurationSeconds=900
               )
               newsession_id = stsresponse["Credentials"]["AccessKeyId"]
               newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
               newsession_token = stsresponse["Credentials"]["SessionToken"]
               #print ("newsession_id {}:newsession_key{}:newsession_token{}".format(newsession_id,newsession_key,newsession_token))
               iam_assumed_client = boto3.client(
                   'iam',
                    aws_access_key_id=newsession_id,
                    aws_secret_access_key=newsession_key,
                    aws_session_token=newsession_token
                )
               rolesResponse = iam_assumed_client.list_roles(MaxItems=1000)
               for r in [r for r in rolesResponse['Roles'] if '/aws-service-role/' not in r['Path'] and '/service-role/' not in r['Path']]:
                   jobId = client.generate_service_last_accessed_details(Arn=r['Arn'])['JobId']

                   roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
                   jobAttempt = 0
                   while roleAccessDetails['JobStatus'] == 'IN_PROGRESS':
                       time.sleep(jobAttempt*2)
                       jobAttempt = jobAttempt + 1
                       roleAccessDetails = client.get_service_last_accessed_details(JobId=jobId)
                   if roleAccessDetails['JobStatus'] == 'FAILED':
                       # report += 'Unable to retrive last access report for role {0}. No action taken.\n'.format( r['Arn'])
                       print(f'Unable to retrive last access report for role {0}. No action taken.\n')
                   else:
                       lastAccessedDates = [a['LastAuthenticated'] for a in roleAccessDetails['ServicesLastAccessed'] if 'LastAuthenticated' in a]
                       myarn=r['Arn']
                       #print(f'{myarn} LastAccess={lastAccessedDates}')
                       # not accessed in 400days
                       if not lastAccessedDates:
                           #report += 'Role {0} has no access history. No action taken.\n'.format( r['Arn'])
                           print(f'{myarn} has no access history in 400days --delete.')
                       else:
                          roleLastUsed = min(lastAccessedDates)
                          daysSinceUsed = (today - roleLastUsed.replace(tzinfo=None)).days
                          ### add Logic for math to delete if not accessed in X days
                          print(f'{myarn} days since used = {daysSinceUsed} --skip')


            except botocore.exceptions.ClientError as e:
                      assumerole_error = "ErrorAssumeRole"
                      policy_age =  delta_time.days
                      output_csvline(dest_account_id,dest_account_name,dest_account_env,policy_name,dryrun, \
                                    assumerole_error,policy_isdefault,action,policy_version,policy_age,formatted_policy_create_date)
            else:
               print (f'SKIP enviroment={enviroment} dest_account_env={dest_account_env} account={dest_account_name} csvinputenv={dest_account_env} ')
               continue

outputfile.close()
