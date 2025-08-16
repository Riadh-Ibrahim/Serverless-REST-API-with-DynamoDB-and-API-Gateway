import boto3
import json
import os
import logging
from collections import defaultdict

client = boto3.client('dynamodb', region_name='us-east-1')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def to_json(items):
    result = defaultdict(list)
    for item in items:
        f = {
            "fileID": item["fileID"]["S"],
            "taskID": item["taskID"]["S"],
            "fileName": item["fileName"]["S"],
            "filePath": item["filePath"]["S"],
        }
        # Optional fields
        if "uploadedAt" in item and "S" in item["uploadedAt"]:
            f["uploadedAt"] = item["uploadedAt"]["S"]
        if "tags" in item:
            # could be SS or L, handle both defensively
            if "SS" in item["tags"]:
                f["tags"] = item["tags"]["SS"]
            elif "L" in item["tags"]:
                f["tags"] = [v.get("S") or v.get("N") or v.get("BOOL") for v in item["tags"]["L"]]
        # Include priority in the response if it exists
        if "priority" in item:
            f["priority"] = item["priority"].get("S") or item["priority"].get("N")
        result["files"].append(f)
    return result

def query_task_attachments(task_id: str):
    # Query GSI by taskID
    response = client.query(
        TableName=os.environ['TASKFILES_TABLE'],
        IndexName='taskIDIndex',
        KeyConditions={
            'taskID': {
                'AttributeValueList': [{'S': task_id}],
                'ComparisonOperator': "EQ"
            }
        }
    )
    logging.info(response.get("Items", []))
    return json.dumps(to_json(response.get("Items", [])))

def lambda_handler(event, context):
    logger.info(event)
    task_id = event["pathParameters"]["taskID"]
    logger.info(f"Getting all attachments for task {task_id}")
    items = query_task_attachments(task_id)
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://todo.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Content-Type': 'application/json'
        },
        'body': items
    }
