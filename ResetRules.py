import json
import boto3
import datetime
import sys
import logging
from botocore.vendored import requests

log = logging.getLogger()
log.setLevel(logging.INFO)

ec2 = boto3.client("ec2", region_name='us-east-2')

default_secgrp = ec2.describe_security_groups(Filters=[ { 'Name' : 'group-name', 'Values': ["default"] }])['SecurityGroups'][0]
print (default_secgrp)

def lambda_handler(event, context):
	if event['RequestType'] == 'Create':
		mycode()
	response = send(event, context, "SUCCESS", {}, None)
	return {"Response" : response}

def send(event, context, responseStatus, responseData, physicalResourceId):
	responseUrl = event['ResponseURL']

	log.info("Event: " + str(event))
	log.info("ResponseURL: " + responseUrl)

	responseBody = {}
	responseBody['Status'] = responseStatus
	responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
	responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
	responseBody['StackId'] = event['StackId']
	responseBody['RequestId'] = event['RequestId']
	responseBody['LogicalResourceId'] = event['LogicalResourceId']
	responseBody['Data'] = responseData

	json_responseBody = json.dumps(responseBody)

	log.info("Response body: " + str(json_responseBody))

	headers = {'content-type' : "",'content-length' : str(len(json_responseBody))}

	try:
		response = requests.put(responseUrl, data=json_responseBody, headers=headers)
		log.info("Status code: " + str(response.reason))
		return "SUCCESS"
	except Exception as e:
		log.error("send(..) failed executing requests.put(..): " + str(e))
		return "FAILED"

default_secgrp = ec2.describe_security_groups(Filters=[ { 'Name' : 'group-name', 'Values': ["default"] }])['SecurityGroups'][0]
print (default_secgrp)

def revoke_ingress_rules(default_sg):
	print ("------------------------------------------------")
	print ("Revoking Ingress Rules ")
	print (default_sg['GroupId'])
	# Remove the default egress rule
	
	# If the SecGroup has Inbound rules then execute
	if len(default_sg['IpPermissions']) > 0:
		for permission in default_sg['IpPermissions']:
			print (permission)
			try:
				response = ec2.revoke_security_group_ingress(GroupId=default_sg['GroupId'],IpPermissions=[permission])
				print (response)
			except ClientError as e:
				print(e)

def revoke_egress_rules(sgid):
	"""Delete a security group egress rule."""
	print ("------------------------------------------------")
	print ("Revoking Egress Rules ")
	params = {}
	params["GroupId"] = sgid
	params["IpPermissions"] = [{
		"IpProtocol": "-1",
		"FromPort": -1,
		"ToPort": -1,
		"IpRanges": [{"CidrIp": "0.0.0.0/0"}],
		}]
	print(ec2.revoke_security_group_egress(**params))

def add_ingress_rules(sgid):
	print ("------------------------------------------------")
	print ("Adding Ingress Rules ")
	try:
		data = ec2.authorize_security_group_ingress(
			GroupId=sgid,
			IpPermissions=[
				{'IpProtocol': '-1',
				'FromPort': -1,
				'ToPort': -1,
				'IpRanges': [{'CidrIp': '10.0.0.0/8'}, {'CidrIp': '172.16.0.0/12'}, {'CidrIp': '192.168.0.0/16'}]},
			])
		print('Ingress Successfully Set %s' % data)
	except ClientError as e:
		print(e)
		
def add_egress_rules(sgid):
	print ("------------------------------------------------")
	print ("Adding Egress Rules ")
	try:
		data = ec2.authorize_security_group_egress(
			GroupId=sgid,
			IpPermissions=[
				{'IpProtocol': '-1',
				'FromPort': -1,
				'ToPort': -1,
				'IpRanges': [{'CidrIp': '10.0.0.0/8'}, {'CidrIp': '172.16.0.0/12'}, {'CidrIp': '192.168.0.0/16'}]},
			])
		print('Egress Successfully Set %s' % data)
	except ClientError as e:
		print(e)

def mycode():
	revoke_ingress_rules(default_secgrp)
	add_ingress_rules(default_secgrp['GroupId'])
	revoke_egress_rules(default_secgrp['GroupId'])
	add_egress_rules(default_secgrp['GroupId'])
	print("Done!")