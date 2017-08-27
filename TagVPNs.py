import json
import boto3
import datetime
import sys
import logging
from botocore.vendored import requests

ec2 = boto3.client('ec2')

log = logging.getLogger()
log.setLevel(logging.INFO)



def lambda_handler(event, context):
	tagvpns()
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



def tagvpns():

	tunnelsdict = ec2.describe_vpn_connections()
	tunnelslist = tunnelsdict['VpnConnections']
	resourcelist=[]
	taglist=[]
	tag={}
	tag2 = {}
	counter = 0
	for tunnel in tunnelslist:
		resourcelist.append(tunnel['VpnConnectionId'])
		counter += 1
	tag['Key']='ENVUID'
	tag['Value']='COREIT'
	taglist.append(tag)
	tag2['Key']='appci'
	tag2['Value']='transit'
	taglist.append(tag2)
	print("Adding Tags " + str(taglist))
	ec2.create_tags(Resources=resourcelist, Tags=taglist)
	print ("Updated " + str(counter) + " VPN Connections")
