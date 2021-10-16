import boto3
import time
import json

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
tableName = "TickPrices1"

def create_table(dynamodb=None):
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'currency',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'tickTime',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'tickTime',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'currency',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    print("Table status:", table.table_status)
    return table

def add_some_data(client):
    # item = {
    #     'tickTime': { int(time.time())},
    #     'prices': {}
    #     }
    # return
    with open("miniticker.json", "r") as fileHandler:
        stuff = json.loads(fileHandler.read())

    print("_-----")
    print(len(stuff))
    for line in stuff:
        itemToInsert = {
            "tickTime": {"N": str(line["E"])},
            "currency": {"S": line["s"]},
            "values": {"S": str(line)}
        }
        print(itemToInsert)
        response = client.put_item(
            TableName=tableName, 
            Item=itemToInsert
        )
        print(response)



if __name__ == '__main__':
    # movie_table = create_table(dynamodb)
    add_some_data(client)