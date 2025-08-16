import boto3
import json
import os
import logging

dynamo = boto3.client('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

bucket = os.environ['TASKFILES_BUCKET']
bucket_cdn = os.environ['TASKFILES_BUCKET_CDN']

def delete_s3_object(key: str):
    response = s3.delete_object(
        Bucket=bucket,
        Key=key,
    )
    logging.info(f"{key} deleted from S3")
    return response

def delete_dynamo_record(file_id: str):
    response = dynamo.delete_item(
        TableName=os.environ['TASKFILES_TABLE'],
        Key={'fileID': {'S': file_id}}
    )
    logging.info(f"{file_id} deleted from DynamoDB")
    return response

def lambda_handler(event, context):
    logger.info(event)

    event_body = json.loads(event["body"])
    path_params = (event.get('pathParameters') or {})
    attachment_id = path_params.get('attachmentID') or path_params.get('fileID')  # backward compatible
    task_id = path_params.get('taskID')

    file_path = event_body["filePath"]  # should be the CDN URL we returned earlier
    # Convert CDN URL back to S3 key
    file_key = str(file_path).replace(f'https://{bucket_cdn}/', '').replace('%40', '@')

    logger.info(f"Deleting file {attachment_id} for task {task_id}")
    delete_s3_object(file_key)
    delete_dynamo_record(attachment_id)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://todo.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET, DELETE, POST, OPTIONS',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({"status": "success"})
    }
