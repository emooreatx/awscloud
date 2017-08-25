from __future__ import print_function

import json
import boto3
import logging

#setup simple logging for INFO
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

#define the connection region
rds = boto3.client('rds', region_name="us-east-2")

def lambda_handler(event, context):

	databasesdict=rds.describe_db_instances()
	databaseslist=databasesdict['DBInstances']
	for database in databaseslist:
		if database['LicenseModel'] == "bring-your-own-license":
			print("Deleting " + database['DBInstanceIdentifier'])
			rds.delete_db_instance(DBInstanceIdentifier=database['DBInstanceIdentifier'],SkipFinalSnapshot=True)
		else:
			print("Skipping " + database['DBInstanceIdentifier'])
		
		
