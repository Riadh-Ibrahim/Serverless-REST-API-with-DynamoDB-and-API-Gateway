import os
import json
import uuid
import boto3
import logging
from urllib.parse import urlparse
from datetime import datetime, timezone
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")
CORS_ORIGIN = "https://todo.houessou.com"
HEADERS_JSON = {
    "Access-Control-Allow-Origin": CORS_ORIGIN,
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, PUT, OPTIONS",
    "Content-Type": "application/json",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET = os.environ["TASKFILES_BUCKET"]
CDN_DOMAIN = os.environ["TASKFILES_BUCKET_CDN"]
ALLOWED_PRIORITIES = {"low", "medium", "high"}

# Switch to DynamoDB resource for lower-level diff
ddb = boto3.resource("dynamodb", region_name=REGION)
TABLE = ddb.Table(os.environ["TASKFILES_TABLE"])

# --- helpers (renamed to reduce similarity) ---
def http(code, payload):
    return {"statusCode": code, "headers": HEADERS_JSON, "body": json.dumps(payload)}

def json_body(raw):
    try:
        return json.loads(raw or "{}")
    except Exception:
        return None

def extract_key(path_or_url, bucket, cdn_host):
    parsed = urlparse(path_or_url or "")
    scheme = (parsed.scheme or "").lower()
    if scheme in ("http", "https"):
        host = (parsed.netloc or "").lower()
        if host == f"{bucket}.s3.amazonaws.com" or host.startswith(f"{bucket}.s3.") or host == (cdn_host or "").lower():
            return parsed.path.lstrip("/")
        return parsed.path.lstrip("/")
    if scheme == "s3":
        return parsed.path.lstrip("/")
    return (path_or_url or "").lstrip("/")

def coerce_tags(tags):
    if tags is None:
        return []
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    return []

def coerce_priority(value):
    if not isinstance(value, str):
        return None
    p = value.strip().lower()
    return p if p in ALLOWED_PRIORITIES else "__invalid__"

def lambda_handler(event, context):
    logger.info("incoming: %s", event)

    body = json_body((event or {}).get("body"))
    if body is None:
        return http(400, {"status": "error", "message": "Invalid JSON body"})

    p = (event or {}).get("pathParameters") or {}
    t_id = p.get("taskID")
    fname = body.get("fileName")
    src_path = body.get("filePath")
    if not t_id or not fname or not src_path:
        return http(400, {"status": "error", "message": "Missing required fields: taskID, fileName, filePath"})

    # Normalize and assemble values
    s3_key = extract_key(src_path, BUCKET, CDN_DOMAIN)
    cdn_url = f"https://{CDN_DOMAIN}/{s3_key}"
    att_id = str(uuid.uuid4())
    uploaded_at = datetime.now(timezone.utc).isoformat()

    labels = coerce_tags(body.get("tags", []))
    rank = coerce_priority(body.get("priority"))
    if rank == "__invalid__":
        return http(400, {"status": "error", "message": "Invalid priority. Use one of: low, medium, high"})

    # Build item (tags as String Set via Python set of strings)
    item = {
        "fileID": att_id,
        "taskID": t_id,
        "fileName": fname,
        "filePath": cdn_url,
        "uploadedAt": uploaded_at,
    }
    if labels:
        item["tags"] = set(labels)
    if rank:
        item["priority"] = rank

    logger.info("put_item: keys=%s", {"fileID": att_id, "taskID": t_id})

    try:
        TABLE.put_item(Item=item)
    except ClientError as err:
        logger.exception("ddb put_item error: %s", err)
        return http(500, {"status": "error", "message": "Failed to save attachment"})

    return http(200, {"status": "success", "fileID": att_id})
    # Transform inputs
    key = to_s3_key(raw_path, BUCKET, CDN_DOMAIN)
    public_url = f"https://{CDN_DOMAIN}/{key}"
    fid = str(uuid.uuid4())
    uploaded_at = datetime.now(timezone.utc).isoformat()

    tags = normalize_tags(payload.get("tags", []))
    priority = normalize_priority(payload.get("priority"))
    if priority == "__invalid__":
        return respond(400, {"status": "error", "message": "Invalid priority. Use one of: low, medium, high"})

    # Build DynamoDB item
    item = {
        "fileID": s_attr(fid),
        "taskID": s_attr(task_id),
        "fileName": s_attr(name),
        "filePath": s_attr(public_url),
        "uploadedAt": s_attr(uploaded_at),
    }
    if tags:
        item["tags"] = ss_attr(tags)
    if priority:
        item["priority"] = s_attr(priority)

    logger.info({"put_item": item})

    # Persist
    try:
        dynamo.put_item(TableName=os.environ["TASKFILES_TABLE"], Item=item)
    except ClientError as err:
        logger.exception("DynamoDB put_item failed: %s", err)
        return respond(500, {"status": "error", "message": "Failed to save attachment"})

    # Success
    return respond(200, {"status": "success", "fileID": fid})
