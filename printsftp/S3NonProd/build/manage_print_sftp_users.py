#!/usr/bin/env python3
#2/24/2022-2

#HOST              = "virprintsftpctlrdev"
#s3bucket          = "virdjifprintsftpcf-dev"
#EFS               =  "fs-08ef52d098c60b174"
# https://stackoverflow.com/questions/58042594/aws-secret-cant-be-converted-into-key-names-and-value-pairs
# https://stackoverflow.com/questions/69877084/the-secret-value-cant-be-converted-to-key-name-and-value-pairs
import boto3  # Required to interact with AWS
import json   # Required for return object parsing
import sys, pwd, string, os, crypt, fileinput, subprocess
from fileinput import FileInput
from datetime import datetime
from pwd import getpwnam
from os import system, name
from random import *
from subprocess import call
from time import sleep
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from botocore.exceptions import ClientError
# http://beta.awsdocs.com/services/secrets_manager/using_secrets_manager/
# pwgen -sBv 15 1

# Set required variables
rundate = datetime.today().strftime('%Y%m%d%H%M%S')
userjasonfile = "/home/control/json_templates/sftp_readonly.json-%s" % rundate
#    with open(r"json_templates/sftp_readonly.json-%s" % rundate, 'w') as file:
s3bucket = "virdjifprintsftpcf-dev"
secret_name = "s-d7c09827fb0c47e2a/"
endpoint_url = "https://secretsmanager.us-east-1.amazonaws.com"
region_name = "us-east-1"
efs = "fs-08ef52d098c60b174"
transfer_server = "s-d7c09827fb0c47e2a/"
role = "arn:aws:iam::453286311137:role/djprint-sftpclient-readonly-role"


# randon passwd generator
def gen_password():
    characters = string.ascii_letters + string.digits
    password =  "".join(choice(characters) for x in range(randint(16, 16)))
    return password

#clear screen function
def clear():
    # check and make call for specific operating system
    _ = system('clear')


# operation main menu
def operator_menu():
    choice = input("""
                A. list (A)ll users
                L. (L)ist specific user
                C. (C)reate new user
                D. (Delete) user -- Not available. Contact Systems Administration
                E. (E)xit

                Please enter A,L,C or E : """)
    if choice == "A" or choice == "a":
         list_all_users()
    elif choice =="L" or choice == "l":
         single_user = input("Enter sftp username: ")
         list_single_user(single_user)
    elif choice == "C" or choice == "c":
         create_user()
    elif choice == "D" or choice == "d":
         print("Deleting a user is currently disabled. Contact Systems Administration")
         print("Exiting")
         exit()
    elif choice == "E" or choice == "e":
         exit()
    else:
         print(f"                Invalid entry > {choice} please enter A,L or C ")
         operator_menu()


def list_single_user(user_name):
    user_secret_id = transfer_server + user_name
    try:
        user_details = client.get_secret_value(SecretId=user_secret_id)
        aws_user = user_details['Name']
        os_username = aws_user.rpartition('/')[-1]
        foundacct_error = "False"

        if os_username in [entry.pw_name for entry in pwd.getpwall()] :
           user_uid = pwd.getpwnam(os_username).pw_uid
           user_gid = pwd.getpwnam(os_username).pw_gid
        else:
           foundacct_error = "True"

        aws_user_acct_details = json.loads(cache.get_secret_string(aws_user))
        pw = aws_user_acct_details['Password']
        role = aws_user_acct_details['Role']
        rolestripped = role.split("/")[-1:]

        homedir = aws_user_acct_details['HomeDirectoryDetails']
        start_marker = '['
        end_marker = ']'
        start_homedir = homedir.index(start_marker) + len(start_marker)
        end_homedir = homedir.index(end_marker, start_homedir + 1)
        homedir = homedir[start_homedir:end_homedir]
        homedir_dict = json.loads(homedir)
        homedir = homedir_dict['Target']
        user_uid_gid = json.loads(aws_user_acct_details['PosixProfile'])
        aws_uid = user_uid_gid['Uid']
        aws_gid = user_uid_gid['Gid']

        print(f'os username: \t\t {os_username}')
        print(f'sftp user:  \t\t {aws_user}')
        print(f'Role: \t\t\t {rolestripped}')
        print(f'Transfer_server: \t {transfer_server}')
        print(f'Aws_home_directory: \t {homedir}')
        #print(f'OS: \t\t {homedir}')
        if foundacct_error != "True":
           os_homedir = os.path.expanduser(f"~{os_username}")
           #print(f'os username:{os_username} \t\t aws transfer username: {aws_user}')
        else:
           os_homedir="Error"
           user_uid="Error" 
           user_gid="Error" 
           os_homedir="Error"
           print()
           print(f'Error: OS Account for {os_username} does not exist')
        print(f'os_home \t\t {os_homedir}')
        print(f'os_uid={user_uid} \t\t aws_uid {aws_uid}')
        print ("#############################################")
    except ClientError as e :
        print(f'AWS Transfer user {user_name} does not exist')
 


def list_all_users ():
    print ("\n""#############################################")
    response = client.list_secrets(
        MaxResults=100,
        SortOrder='asc',
        Filters=[
            {
                'Key': 'tag-value',
                'Values': ['print-sftp']
            }
         ]
       )
    for user_details in response['SecretList']:
        aws_user = user_details['Name']
        os_username = aws_user.rpartition('/')[-1]
        foundacct_error = "False"

        if os_username in [entry.pw_name for entry in pwd.getpwall()] :
           user_uid = pwd.getpwnam(os_username).pw_uid
           user_gid = pwd.getpwnam(os_username).pw_gid
        else:
           foundacct_error = "True"

        aws_user_acct_details = json.loads(cache.get_secret_string(aws_user))
        pw = aws_user_acct_details['Password']
        role = aws_user_acct_details['Role']
        rolestripped = role.split("/")[-1:]

        homedir = aws_user_acct_details['HomeDirectoryDetails']
        start_marker = '['
        end_marker = ']'
        start_homedir = homedir.index(start_marker) + len(start_marker)
        end_homedir = homedir.index(end_marker, start_homedir + 1)
        homedir = homedir[start_homedir:end_homedir]
        homedir_dict = json.loads(homedir)
        homedir = homedir_dict['Target']
        user_uid_gid = json.loads(aws_user_acct_details['PosixProfile'])
        aws_uid = user_uid_gid['Uid']
        aws_gid = user_uid_gid['Gid']

        print(f'os username: \t\t {os_username}')
        print(f'sftp user:  \t\t {aws_user}')
        print(f'Role: \t\t\t {rolestripped}')
        print(f'Transfer_server: \t {transfer_server}')
        print(f'Aws_home_directory: \t {homedir}')
        if foundacct_error != "True":
           os_homedir = os.path.expanduser(f"~{os_username}")
        else:
           os_homedir="Error"
           user_uid="Error" 
           user_gid="Error" 
           os_homedir="Error"
           print()
           print(f'Error: OS Account for {os_username} does not exist')
        print(f'os_home \t\t {os_homedir}')
        print(f'os_uid={user_uid} \t\t aws_uid {aws_uid}')
        print(f'os_gid={user_gid} \t\t aws_gid {aws_gid}')
        print ("#############################################")

def add_transfer_user_tags(aws_secret_id):
    try:
        response = client.tag_resource(
                SecretId=aws_secret_id,
                Tags=[
                    { 'Key': 'TransferServer', 'Value': 's-d7c09827fb0c47e2a' },
                    { 'Key': 'application',    'Value': 'print-sftp' },
                    { 'Key': 'envirnoment',     'Value': 'nonprod' },
                    { 'Key': 'appid',          'Value': 'prt_pub_pas' },
                    { 'Key': 'bu',             'Value': 'djprt' },
                    { 'Key': 'component',      'Value': 'backend' },
                    { 'Key': 'owner',          'Value': 'printit@dowjones.com' },
                    { 'Key': 'description',    'Value': 'print-sftp' },
                    { 'Key': 'product',        'Value': 'adv' }
                 ]
        )
    except ClientError as e :
           print('User tagging issue')

def add_transfer_user(username,userdir,userpasswd):
    cryptedpasswd = crypt.crypt(userpasswd,"hk7fv97RsKnnLcb")
    os.system("useradd \
    --create-home \
    --home "+userdir+" \
    --comment \"print-sftp-user\" \
    --gid 10000 \
    --shell /sbin/nologin \
    --password "+cryptedpasswd+" "+username+" ")
    os.system("chmod 770 "+userdir+"")
    user_uid = getpwnam(username).pw_uid
    user_gid = getpwnam(username).pw_gid
    print(f'OS level Complete: username={username} uid={user_uid} gid={user_gid} directory={userdir}')

    with open(r'/home/control/json_templates/sftp_readonly.json', 'r') as file:
         data = file.read()
         data = data.replace('CHANGE_PASSWD', userpasswd)
         data = data.replace('CHANGE_USER', username)
         data = data.replace('CHANGE_UID', str(user_uid))
    userjasonfile = "/home/control/json_templates/sftp_readonly.json-%s" % rundate
    with open(f"{userjasonfile}", 'w') as file:
         file.write(data)
         os.system("chmod 770 "+userjasonfile+"")
         file.close()
    secretname = transfer_server + username
    inputjson = "file://" + str(userjasonfile)
    os.system("/usr/local/bin/aws secretsmanager create-secret --name  "+secretname+" --secret-string "+inputjson+" ")
    os.remove(""+userjasonfile+"")
    add_transfer_user_tags(secretname)

def getnewuserinfo():
    newpwkey = str("generate")
    awsuser_exist = "True"
    while awsuser_exist == "True":
       username = str(input("Enter username: "))
       while not (username.isalnum()):
           print(f'username {username} invalid. must be alphanumeric')
           username = str(input("Enter username: "))

       secret_name = str(transfer_server + username)
       print(f'secret_name = {secret_name}')
       try:
          userexist_response = cache.get_secret_string( secret_name )
          awsuser_exist = "True"
          print(f'user {username} already exists within aws transfer')
          #print(f'userexist_response = {userexist_response}')
       except ClientError as e :
          awsuser_exist = "False"

    while username in [entry.pw_name for entry in pwd.getpwall()] :
        print(f'ERROR: user {username} already exists')
        username = str(input("Enter username: "))

    userdir  = "/sftp/print/" + username
    userpasswd  = str(input("\n\nEnter user passwd OR >> \"gen|generate\" << for system generated: "))
    if userpasswd.casefold() == newpwkey.casefold() or userpasswd.casefold() == "gen":
       userpasswd = gen_password()
    else:
        while len(userpasswd) < 8 :
          if userpasswd.casefold() == newpwkey.casefold() or userpasswd.casefold() == "gen":
             userpasswd = gen_password()
          else:
             print('Password length to short')
             userpasswd  = str(input("\n\nEnter user passwd OR >> \"gen|generate\" << for system generated: "))
    return username, userdir, userpasswd 


def confirm_newuser(username,userdir,userpasswd):
    confirmed_ok = "Y"
    print (f'username = {username}')
    print (f'userdir = {userdir}')
    print (f'userpassword = {userpasswd}')
    confirmation = str(input("\n\nProceed Y|y : "))
    if confirmation.casefold() != confirmed_ok.casefold():
        sys.exit("Did not receive Y to proceed. Exiting...")
    else:
        add_transfer_user(username,userdir,userpasswd)

def create_user():
    username, userdir, userpasswd = getnewuserinfo()
    confirm_newuser(username,userdir,userpasswd)

# MAIN
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
    endpoint_url=endpoint_url
)
cache = SecretCache(SecretCacheConfig(),client)
clear()
operator_menu()

