#backup code that combines both sqs and s3
#sudo yum install python3-pip
#pip3 install boto3

import boto3
import os
import time


# Initialize Boto3 clients
s3_client = boto3.client('s3', region_name='us-east-1')
sqs_client = boto3.client('sqs', region_name='us-east-1')

# Directory containing image files
image_directory = '/home/ec2-user/images'

# S3 bucket name
bucket_name = 'buckets2038600'

# SQS queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/607200637845/SqsS2038600'

# Function to upload image files to S3 bucket and publish messages to SQS queue
def upload_images():
    uploaded_image = []
    for filename in os.listdir(image_directory):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            try:
                # Upload image file to S3 bucket
                s3_client.upload_file(os.path.join(image_directory, filename), bucket_name, filename)
                print(f"Uploaded {filename} to the S3 bucket successfully.")
                
                # Publish message to SQS queue with filename as vehicle name attribute
                response = sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=f"Successfully uploaded {filename} to the S3 bucket: {bucket_name}.",
                    MessageAttributes={
                        'VehiculeName': {
                            'DataType': 'String',
                            'StringValue': filename  # Use filename without splitting
                        }
                    }
                )
                print(f"Message of {filename} successfully published to SQS queue.")
                print(f"MessageId: {response['MessageId']}")

                uploaded_image.append(filename)
                print("30 seconds before uploading the next image...\n")
                time.sleep(30)   # Wait for 30 seconds before uploading the next image 
            except Exception as e:
                print(f"Failed to upload '{filename}' to S3 bucket '{bucket_name}': {str(e)}")
                print("Continuing to the next image...\n")
    if len(uploaded_image) == len(os.listdir(image_directory)):
        print("\nSUCCESS! ALL IMAGES UPLOADED to the S3 bucket \n")


# Function to continuously upload images
def main():
    while True:
        upload_images()
        print("30 seconds before uploading the next image...\n")
        time.sleep(30)  # Wait for 30 seconds before uploading the next image

if __name__ == "__main__":
    main()
