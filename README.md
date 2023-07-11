# DynamoDB Table Migration with AWS Step Functions, AWS Lambda, and DynamoDB Streams

This repository provides a solution for migrating existing items in a DynamoDB table using AWS Step Functions, AWS Lambda, and DynamoDB Streams. The solution is designed to handle large DynamoDB tables and avoid timeouts that can occur when processing a large number of items. It also provides robust error handling and can recover from failures.

This solution is based on this awesome work and blog post by [Dan Stanhope](https://dev.to/danstanhope/migrating-dynamodb-data-using-lamba-streams-2e3m).

## Overview

The solution works by triggering a Lambda function to scan and update items with a new attribute `pre_existing_processed` in a DynamoDB table. The updates to the items trigger DynamoDB Streams, which can be processed by another Lambda function to perform further actions, such as replicating the changes to another database.

If the table has a large number of existing items, a Step Function is used to manage the migration process and ensure that all items are processed. The Lambda function scans the table, updates the items, and returns the last evaluated key. The Step Function then checks if there are more items to process and, if so, invokes the Lambda function again with the last evaluated key.

## Repository Structure

- `template.yaml`: This is the CloudFormation template that sets up the entire solution. It creates the necessary AWS resources, including the DynamoDB table, the Lambda function, and the Step Function.

- `index.py`: This is the code for the Lambda function. It is written in Python and uses the Boto3 library to interact with AWS services.

## Deployment

To deploy the solution, follow these steps:

1. Clone this repository to your local machine.
2. Navigate to the repository directory.
3. Run the following command to deploy the CloudFormation stack:

```
aws cloudformation deploy --template-file template.yaml --stack-name MyStack --capabilities CAPABILITY_IAM
```

Replace `MyStack` with the name you want to give to your stack.

## Usage

Once the solution is deployed, you can start the migration process by start executing the Step Function. The Lambda function will scan the DynamoDB table, update the items, and return the last evaluated key. The Step Function will then check if there are more items to process and, if so, invoke the Lambda function again with the last evaluated key.

## Error Handling

The solution includes robust error handling. The Step Function includes a Retry policy that retries the Lambda function up to 5 times with an interval of 5 seconds between each attempt, and a Catch block that transitions the state machine to a Fail state if the Lambda function throws an error after all retry attempts.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
