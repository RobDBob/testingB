import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://5436b091-0ee0-4-231-b9ee.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'Gnw7vrmbeH9Amp7ZqHX7RPBCdQaugBEQfWTITmSDDCnNeEycsFFjy6RfYcLROhVhEG2EtFXpgF7RNFUoXvA2dg=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'SampleDB'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'ItemsPer3Min'),
}