from os import environ

ENV = environ.get('ENV')

if ENV is not 'development' and ENV is not 'testing' and ENV is not 'production':
    print(f'Invalid ENV value: {ENV}')
    exit(1)


DB_NAME = 
DB_HOST = 
DB_PORT = 
DB_USER =
DB_PASSWORD = 
