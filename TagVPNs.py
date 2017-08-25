import json
import boto3
import datetime
import sys

ec2 = boto3.client('ec2')

def lambda_handler(event, context):

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
	print("Adding Tags " + taglist)
	ec2.create_tags(Resources=resourcelist, Tags=taglist)
	print ("Updated " + str(counter) + " VPN Connections")
