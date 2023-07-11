import os
import boto3
import signal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
table_name = os.environ["TABLE_NAME"]
batch_limit = int(os.environ["BATCH_LIMIT"])
if batch_limit < 0:
    batch_limit = 0


def timeout_handler(signum, frame):
    raise Exception("Lambda function timed out")


def scan_table(table_name, start_key=None):
    table = dynamodb.Table(table_name)
    if start_key:
        response = table.scan(
            FilterExpression=Attr("pre_existing_processed").not_exists(),
            ExclusiveStartKey=start_key,
        )
    else:
        response = table.scan(
            FilterExpression=Attr("pre_existing_processed").not_exists()
        )
    return response


def batch_update_items(items, table_name):
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            item["pre_existing_processed"] = "yes"
            batch.put_item(Item=item)


def migrate_data(last_evaluated_key=None):
    try:
        response = scan_table(table_name, last_evaluated_key)
        batch_update_items(response["Items"], table_name)
        batch_count = 1
        while "LastEvaluatedKey" in response:
            if batch_limit and batch_count >= batch_limit:
                break
            response = scan_table(table_name, response["LastEvaluatedKey"])
            batch_update_items(response["Items"], table_name)
            batch_count += 1
        print("Migration completed successfully.")
        return {
            "status": "success",
            "LastEvaluatedKey": response.get("LastEvaluatedKey", None),
        }
    except ClientError as e:
        print(e.response["Error"]["Message"])
        return {"status": "error", "message": e.response["Error"]["Message"]}


def lambda_handler(event, context):
    # Set up a timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(context.get_remaining_time_in_millis() // 1000 - 1))

    # Get LastEvaluatedKey from event input
    last_evaluated_key = event.get("LastEvaluatedKey", None)

    # Start the migration task
    result = migrate_data(last_evaluated_key)

    # Check the result and raise an exception if an error occurred
    if result["status"] == "error":
        raise Exception(result["message"])

    return result


signal.signal(signal.SIGALRM, timeout_handler)
