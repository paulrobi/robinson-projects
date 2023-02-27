#!/bin/bash -v
exec &> >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo ECS_CLUSTER=ecsec2cluster1 >> /etc/ecs/ecs.config
echo ECS_BACKEND_HOST= >> /etc/ecs/ecs.config

status=1
while [ $status -ne 0 ] ; do
 timeout 5s curl -fIsS http://google.com > /dev/null
 status=$?
 sleep 10
 printf "network not alive yet \n"
done
printf "network alive \n"

yum -y install unzip
yum -y update
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip -q /tmp/awscliv2.zip
sudo ./aws/install -i /usr/local/aws-cli -b /usr/local/bin && /usr/local/bin/aws --version
cat ~/.bash_profile |grep -v ^PATH > /tmp/root_profile;echo "export PATH=/usr/local/sbin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin:/usr/local/bin" >> /tmp/root_profile
cat /tmp/root_profile > ~/.bash_profile
source ~/.bash_profile

HOST="ec2ecs"
REG=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/\(.*\)[a-z]/\1/'`
AZ=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
Iid=`curl http://169.254.169.254/latest/meta-data/instance-id`
ASG=`aws ec2 describe-instances --instance-ids $Iid --region $REG |grep asg|cut -d '"' -f4`
ENIid=`aws  ec2 describe-network-interfaces --region $REG --filters Name=tag:lockname,Values=${HOST}-$AZ-eni |grep NetworkInterfaceId|cut -d'"' -f4`
ENImac=`aws  ec2 describe-network-interfaces --region $REG --network-interface-ids $ENIid|grep MacAddress|cut -d'"' -f4`
ENIip=`aws  ec2 describe-network-interfaces --region $REG --network-interface-ids $ENIid|grep PrivateIpAddress|cut -d'"' -f4|tail -1`
/usr/local/bin/aws  ec2 attach-network-interface --region $REG --network-interface-id $ENIid --instance-id $Iid --device-index 1

sed -i 's/ONBOOT=yes/ONBOOT=no/g' /etc/sysconfig/network-scripts/ifcfg-eth0
printf "network: \n" > /etc/cloud/cloud.cfg.d/custom-networking.cfg
printf "config: disabled \n" >> /etc/cloud/cloud.cfg.d/custom-networking.cfg
/bin/echo "GATEWAYDEV=eth1" >> /etc/sysconfig/network

/bin/cat  > /etc/sysconfig/network-scripts/ifcfg-eth1 << EOF
DEVICE="eth1"
BOOTPROTO="dhcp"
ONBOOT="yes"
TYPE="Ethernet"
USERCTL="yes"
PEERDNS="yes"
IPV6INIT="no"
PERSISTENT_DHCLIENT="1"
NM_CONTROLLED=no
EOF
chmod 0644 /etc/sysconfig/network-scripts/ifcfg-eth1

/bin/hostnamectl set-hostname $HOST-$AZ
echo $HOST-$AZ > /etc/hostname
/sbin/init 6
