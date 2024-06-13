import boto3

# Initialize Boto3 EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# Specify the AMI ID and instance type
ami_id = 'ami-0f403e3180720dd7e'
instance_type = 't2.micro'
key_name = 'vockey'  # Name of the key pair
security_group_name = 'MySSHSecurityGroup'

try:
    # Check if the security group already exists
    response = ec2_client.describe_security_groups(GroupNames=[security_group_name])
    if not response['SecurityGroups']:
        # If the security group doesn't exist, create it
        security_group = ec2_client.create_security_group(
            Description='Allow SSH access',
            GroupName=security_group_name
        )

        # Authorize SSH access on port 22
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group['GroupId'],
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow access from anywhere
                }
            ]
        )
    else:
        # If the security group already exists, use it
        security_group_id = response['SecurityGroups'][0]['GroupId']
        print(f"Using existing security group: {security_group_name} (ID: {security_group_id})")

    # Launch EC2 instance
    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,  # Assign the key pair
        SecurityGroupIds=[security_group_id],  # Use the security group
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'InstanceS2038600'  
                    }
                ]
            }
        ]
    )

    # Extract instance ID from the response
    instance_id = response['Instances'][0]['InstanceId']

    # Wait until the instance is in the 'running' state
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    # Describe the instance to get its public IP address
    instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']

    # Print instance ID and public IP
    print()
    print("EC2 instance with ID", instance_id, "has been created successfully.")
    print("Public IP address:", public_ip)
    print()

except Exception as e:
    print("An error occurred:", str(e))
