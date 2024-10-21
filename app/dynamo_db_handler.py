import boto3
import logging
from botocore.exceptions import BotoCoreError, ClientError

class DynamoDBHandler:
    """Handles DynamoDB operations."""

    def __init__(self, table_name='MembershipData', region=None, endpoint_url=None):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=region or 'us-west-2',
            endpoint_url=endpoint_url
        )
        self.table_name = table_name
        self.table = self._initialize_table()

    def _initialize_table(self):
        """
        Initializes and returns the DynamoDB table. If the table does not exist, it is created.
        """
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()  # Try to load the table to confirm its existence
            logging.info(f"Connected to existing table: {self.table_name}")
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            logging.info(f"Table '{self.table_name}' not found. Creating a new one.")
            table = self._create_table(self.table_name)
        except BotoCoreError as e:
            logging.error(f"Error connecting to DynamoDB: {str(e)}")
            raise
        return table

    def _create_table(self, table_name):
        """
        Creates a DynamoDB table if it doesn't exist.
        """
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            table.wait_until_exists()
            logging.info(f"Table '{table_name}' created successfully.")
            return table
        except ClientError as e:
            logging.error(f"Failed to create table '{table_name}': {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error creating table '{table_name}': {str(e)}")
            raise

    def insert_data(self, item):
        """
        Inserts an item into the DynamoDB table.
        """
        try:
            self.table.put_item(Item=item)
            logging.info(f"Successfully inserted item: {item}")
        except ClientError as e:
            logging.error(f"Failed to insert item: {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error inserting item: {str(e)}")
            raise

    def scan_data(self, scan_kwargs=None):
        """
        Scans the DynamoDB table and returns the result.
        """
        scan_kwargs = scan_kwargs or {}
        try:
            response = self.table.scan(**scan_kwargs)
            logging.info(f"Successfully scanned table with params: {scan_kwargs}")
            return response
        except ClientError as e:
            logging.error(f"Failed to scan table: {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error scanning table: {str(e)}")
            raise

    def get_item(self, key):
        """
        Retrieves a single item from the DynamoDB table based on the key.
        """
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            if item:
                logging.info(f"Successfully retrieved item: {item}")
                return item
            else:
                logging.warning(f"No item found with key: {key}")
                return None
        except ClientError as e:
            logging.error(f"Failed to retrieve item: {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error retrieving item: {str(e)}")
            raise

    def update_item(self, key, update_expression, expression_values):
        """
        Updates an item in the DynamoDB table based on the key and update expression.
        """
        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            logging.info(f"Successfully updated item with key: {key}")
            return response
        except ClientError as e:
            logging.error(f"Failed to update item: {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error updating item: {str(e)}")
            raise

    def delete_item(self, key):
        """
        Deletes an item from the DynamoDB table based on the key.
        """
        try:
            self.table.delete_item(Key=key)
            logging.info(f"Successfully deleted item with key: {key}")
        except ClientError as e:
            logging.error(f"Failed to delete item: {e.response['Error']['Message']}")
            raise
        except BotoCoreError as e:
            logging.error(f"Error deleting item: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    handler = DynamoDBHandler(region='us-west-2')

    # Sample data for insertion
    item = {
        'email': 'john.doe@example.com',
        'full_name': 'John Doe',
        'phone': '+14155552671',
        'is_newsletter_subscribed': True
    }

    # Insert, scan, update, and delete operations
    try:
        handler.insert_data(item)
        response = handler.scan_data()
        print("Scan Results:", response.get('Items'))
        
        # Update item
        handler.update_item(
            key={'email': 'john.doe@example.com'},
            update_expression="SET full_name = :new_name",
            expression_values={':new_name': 'Jonathan Doe'}
        )

        # Get updated item
        updated_item = handler.get_item({'email': 'john.doe@example.com'})
        print("Updated Item:", updated_item)

        # Delete item
        handler.delete_item({'email': 'john.doe@example.com'})
    except Exception as e:
        logging.error(f"Operation failed: {str(e)}")
