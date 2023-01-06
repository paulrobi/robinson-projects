import boto3  # Required to interact with AWS
import json   # Required for return object parsing
import sys, pwd, string, os, crypt, fileinput
from fileinput import FileInput
from datetime import datetime
from pwd import getpwnam
from os import system, name
from random import *
from subprocess import call
from time import sleep
from botocore.exceptions import ClientError

scriptdate = datetime.today().strftime('%Y%m%d%H%M%S')
endpoint_url = "https://secretsmanager.us-east-1.amazonaws.com"
region_name = "us-east-1"


session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
    endpoint_url=endpoint_url
)
response = client.describe_secret(
    SecretId='s-d7c09827fb0c47e2a/testuser26'
)
myarn = response['ARN']
#print(response)

with open(r"/home/control/json_templates/sftp_readonly.json-NOW", 'r') as file:
         #SecretString = json.dump(file.read())

print(SecretString[1:-1])

#print(f' ARN IS ::: {myarn}')


'''
def add_transferuser(secret_value_dict):
     secret_value_str = json.dumps(secret_value_dict)
     print(secret_value_str)


username = "paul123"
userpasswd = "NowisTheTime"
userdir = "/sftp/print/testuser100"
secret_name = "s-d7c09827fb0c47e2a/testuser100"
role = "arn:aws:iam::453286311137:role/djprint-sftpclient-readonly-role"
user_uid = "12000"
user_gid = "13000"

with open(r'json_templates/sftp_readonly.json', 'r') as file:
    data = file.read()
    data = data.replace('CHANGE_PASSWD', userpasswd)
    data = data.replace('CHANGE_USER', username)
    data = data.replace('CHANGE_UID', user_uid)


with open(r"json_templates/sftp_readonly.json-%s" % scriptdate, 'w') as file:
    file.write(data)

# Printing Text replaced
print("Text replaced")


#with fileinput.FileInput(files=('json_templates/sftp_readonly.json'), inplace=True, backup='.bak') as file:
#    for line in file:
#        print(line.replace('CHANGE_PASSWD', userpasswd), end='')

#user_secret_value_dict = {
#   'Password': userpasswd,
#   'Role': role,
#   'HomeDirectoryType': 'LOGIGAL',
#   'HomeDirectoryDetails': userdir,
#   'PosixProfile': "{ \"Uid\": user_uid, \"Gid\": user_gid,\"SecondaryGids\": []}"
#    }
#add_transferuser(user_secret_value_dict)
'''
