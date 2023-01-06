#!/bin/bash

myrandom=$(echo $RANDOM)
webalb="djcom-dowjonesweb-webalb"
adminalb="djcom-dowjonesweb-admalb"
region="us-east-1"

printf "\t\t DJCOMWEB NonProd WEB Server STATUS `date` \n"
ALB_ARN=$(aws elbv2 describe-load-balancers --names $webalb --query 'LoadBalancers[0].LoadBalancerArn' --output text)
TG_ARN=$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN --query 'TargetGroups[0].TargetGroupArn' --output text)

cat /dev/null > /tmp/liveinstanceip-$myrandom.txt

#for instance in `aws elb describe-load-balancers --load-balancer-names $webalb --region $region|grep i- |awk -F"\"" '{print $4}'` ; do
for instance in `aws elbv2 describe-target-health --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].Target.Id' --output text` ; do
    aws ec2 describe-instances --instance-ids $instance --region $region --query "Reservations[*].Instances[*].NetworkInterfaces[*].PrivateIpAddress" --output=text >> /tmp/liveinstanceip-$myrandom.txt
done

for ip in `cat /tmp/liveinstanceip-$myrandom.txt`
do
  state=$(curl --silent http://${ip}//sitestate.txt )
  printf "${ip} \t ${state}  \n"
done

printf "\n\n"
printf "\t\t DJCOMWEB  NonProd ADMIN Server STATUS `date` \n"
ALB_ARN=$(aws elbv2 describe-load-balancers --names $adminalb --query 'LoadBalancers[0].LoadBalancerArn' --output text)
TG_ARN=$(aws elbv2 describe-target-groups --load-balancer-arn $ALB_ARN --query 'TargetGroups[0].TargetGroupArn' --output text)
cat /dev/null > /tmp/liveinstanceip-$myrandom.txt
for instance in `aws elbv2 describe-target-health --target-group-arn $TG_ARN --query 'TargetHealthDescriptions[*].Target.Id' --output text` ; do
    aws ec2 describe-instances --instance-ids $instance --region $region --query "Reservations[*].Instances[*].NetworkInterfaces[*].PrivateIpAddress" --output=text >> /tmp/liveinstanceip-$myrandom.txt
done

for ip in `cat /tmp/liveinstanceip-$myrandom.txt`
do
  state=$(curl --silent http://${ip}//sitestate.txt )
  printf "${ip} \t ${state}  \n"
done
/bin/rm -f /tmp/liveinstanceip-$myrandom.txt

