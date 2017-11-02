import json
import boto3
import datetime
import sys
import logging
from botocore.vendored import requests

log = logging.getLogger()
log.setLevel(logging.INFO)

ec2 = boto3.resource('ec2', region_name="us-east-1")

for vpc in ec2.vpcs.all():
	myigws = vpc.internet_gateways.all()
	for igw in myigws:
		vpc.detach_internet_gateway(DryRun=False, InternetGatewayId=igw.id)
		myigw=ec2.InternetGateway(igw.id)
		myigw.delete()
	vpc.delete()
		

print (list(myigws)[0])