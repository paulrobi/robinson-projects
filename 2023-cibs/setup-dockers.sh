#!/bin/sh -vx
#
# check docker instances every NUMSECS seconds for NUMTIMES times
# since this task runs every minute in cron,
#   NUMSECS*NUMTIMES must be < 60
#
#
# api-01 fcibsint  ficibsapp  awsinfomixint.entstagbilling.dowjones.io
# api-02 fcibsint2 ficibsapp2 awsinformixprdcpy.entstagbilling.dowjones.io
# api-03 fcibsint1 ficibsapp1 awsinfomixint.entstagbilling.dowjones.io

# Format:
#   <ECS service name>:<docker hostname>:<EC2 DNS name>:<Informix db fqdn>
# this is for NLB setup
CSNLIST="\
 api-01:fcibsint:ficibsapp:vircibsinformixdbs01,vircibsinformixdbs02,awsinformixint,entstagbilling.dowjones.io       \
 api-02:fcibsint2:ficibsapp2:awsinformixprdcpy,entstagbilling.dowjones.io \
 api-03:fcibsint1:ficibsapp1:vircibsinformixdbs01,vircibsinformixdbs02,awsinformixint,entstagbilling.dowjones.io     \
"
CSNLIST="\
 api-01:fcibsint:ficibsapp:awsinformixint,entstagbilling.dowjones.io       \
 api-02:fcibsint2:ficibsapp2:awsinformixprdcpy,entstagbilling.dowjones.io \
 api-03:fcibsint1:ficibsapp1:awsinformixint,entstagbilling.dowjones.io     \
 api-04:fcibsint3:ficibsapp3:awsinformixint,entstagbilling.dowjones.io     \
"

NUMSECS=3
NUMTIMES=10

PATH=$PATH:/usr/local/bin
PIDFILE=/var/tmp/`basename $0`.lock
SETUPDOCKER=setup-docker-instance.sh
CID=djis-cibs-engine-stag
set -- $CSNLIST
#echo "Number of items to check: $#"

# singleton check
[ -f "$PIDFILE" ] &&  exit 1
touch $PIDFILE

echo Start: `date`
try=0
hits=0
csnhits=
while
  [ $try -lt $NUMTIMES -a $hits -lt $# ]
do
  for csn
  in $CSNLIST
  do
    echo "Checking $csn.."
    csnid=`echo $csn|cut -f1 -d:`
    DNM="${CID}-${csnid}-[0-9].*-main"
    DCI=`docker ps|grep $DNM |awk '{print $1}'`
    if
      [ "$DCI" ]
    then
      echo $csnhits | grep $csnid > /dev/null
      if
        [ $? != 0 ]
      then
        nohup $SETUPDOCKER $csn > /var/tmp/$csnid.nohup.out
        csnhits="$csnhits $csnid"
        hits=`expr $hits + 1`
      fi
    fi
  done
  try=`expr $try + 1`
  sleep $NUMSECS
done

echo End: `date`
rm -f $PIDFILE
