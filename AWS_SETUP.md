# AWS deployment for the inference service

Copy all files in this update into the existing ai-inference-service folder.
Keep the original Dockerfile, requirements.txt, and training_examples.py.

Build a single-architecture Lambda image with Docker Desktop running:

    docker buildx build --platform linux/arm64 --provenance=false --load -f Dockerfile.aws -t ai-inference-lambda .

In US East (Ohio), create a private ECR repository named ai-inference-lambda.
Use ECR's View push commands to authenticate, tag ai-inference-lambda:latest,
and push the image. Keep credentials out of the repository.

Create an on-demand DynamoDB table named inference-logs with request_id
as the String partition key. Create a Lambda Event Function from the ECR
container image, select arm64, and set DYNAMODB_TABLE to inference-logs.
Set memory to 1024 MB and timeout to 20 seconds. Grant the Lambda execution
role dynamodb:PutItem on this table only, alongside its basic logging policy.

Create a Lambda Function URL with NONE authentication if the project needs
public access. Verify GET /docs and POST /predict using a sample review.
Match the returned request_id to a row in DynamoDB. Submit the GitHub URL,
live function URL, and updated report with Swagger and DynamoDB evidence.
