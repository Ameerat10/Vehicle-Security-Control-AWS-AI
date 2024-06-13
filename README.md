# Vehicle-Security-Control-AWS-AI
This project demonstrates a vehicle control application at a security entrance using AWS Artificial Intelligence (AI) services. The application employs AWS Rekognition for label and text detection in image files, simulating a vehicle control system.

# Vehicle Control System at Security Entrance with AWS AI Services

## Features

### Resource Creation

- Use Python (Boto3) and CloudFormation to create an EC2 instance, S3 bucket, SQS queue, and DynamoDB table.

### Image Upload and Lambda Trigger

- Automatically upload image files from EC2 to S3 at 30-second intervals.
- Trigger Lambda functions via SQS to process these images.

### Label and Text Detection

- Lambda functions extract image details and detect vehicle labels and plate numbers using AWS Rekognition.

### Database Update and Notification

- Store image information and detection results in DynamoDB.
- Notify security officers via email for blacklisted or unrecognized vehicles.

## Security and Optimization

- Implements IAM roles and policies for secure access.
- Provides a cost-optimized solution for handling numerous image uploads over extended periods.

