import boto3

# Initialize Boto3 client for DynamoDB
dynamodb_client = boto3.client('dynamodb')

# Name of the DynamoDB table for vehicle records
table_name = 'VehiculeUpdateS2038600'

def create_update_table():
    # Define the attribute definition for the table
    attribute_definitions = [
        {
            'AttributeName': 'VehiucleName',
            'AttributeType': 'S'
        }
    ]

    # Define the key schema for the table
    key_schema = [
        {
            'AttributeName': 'VehiculeName',
            'KeyType': 'HASH'
        }
    ]
    
    # Define the provisioned throughput for the table
    provisioned_throughput = {
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }

    try:
        # Create the DynamoDB table
        dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=attribute_definitions,
            KeySchema=key_schema,
            ProvisionedThroughput=provisioned_throughput
        )
        print(f"\nCreated DynamoDB table: {table_name}\n")
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"DynamoDB table {table_name} already exists")

if __name__ == "__main__":
    create_update_table()
