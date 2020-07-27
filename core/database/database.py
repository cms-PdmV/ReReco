"""
A module that handles all communication with MongoDB
"""
import logging
import time
import json
import os
from pymongo import MongoClient


class Database():
    """
    Database class represents a particular collection in MongoDB
    """

    __DATABASE_HOST = 'localhost'
    __DATABASE_PORT = 27017
    __SEARCH_RENAME = {
        'requests': {
            'runs': 'runs<int>',
            'run': 'runs<int>',
            'workflows': 'workflows.name',
            'workflow': 'workflows.name',
            'output_dataset': 'output_datasets',
        }
    }

    def __init__(self, database_name=None):
        """
        Constructor of database interface
        """
        self.database_name = database_name
        self.logger = logging.getLogger()
        db_host = os.environ.get('DB_HOST', Database.__DATABASE_HOST)
        db_port = os.environ.get('DB_PORT', Database.__DATABASE_PORT)
        db_auth = os.environ.get('DB_AUTH', None)
        username = None
        password = None
        if db_auth:
            with open(db_auth) as json_file:
                credentials = json.load(json_file)

            username = credentials['username']
            password = credentials['password']

        if username and password:
            self.logger.debug('Using DB with username and password')
            self.client = MongoClient(db_host,
                                      db_port,
                                      username=username,
                                      password=password,
                                      authSource='admin',
                                      authMechanism='SCRAM-SHA-256')['rereco']
        else:
            self.logger.debug('Using DB without username and password')
            self.client = MongoClient(db_host, db_port)['rereco']

        self.database = self.client[database_name]

    def get_count(self):
        """
        Get number of documents in the database
        """
        return self.database.count_documents({})

    def get(self, document_id):
        """
        Get a single document with given identifier
        """
        result = self.database.find_one({'_id': document_id})
        if result and 'last_update' in result:
            del result['last_update']

        return result

    def document_exists(self, document_id):
        """
        Do a GET request to check whether document exists
        """
        response = self.get(document_id)
        return bool(response)

    def delete_document(self, document):
        """
        Delete a document
        """
        if not isinstance(document, dict):
            self.logger.error('%s is not a dictionary', document)
            return

        document_id = document.get('_id', '')
        document_id = document_id.strip()
        if not document_id:
            self.logger.error('%s does not have a _id', document)
            return

        self.database.delete_one({'_id': document_id})

    def save(self, document):
        """
        Save a document
        """
        if not isinstance(document, dict):
            self.logger.error('%s is not a dictionary', document)
            return False

        document_id = document.get('_id', '')
        if not document_id:
            self.logger.error('%s does not have a _id', document)
            return False

        document['last_update'] = int(time.time())
        if self.document_exists(document_id):
            self.logger.debug('Updating %s', document_id)
            return self.database.replace_one({'_id': document_id}, document)

        self.logger.debug('Creating %s', document_id)
        return self.database.insert_one(document)

    def query(self,
              query_string=None,
              page=0, limit=20,
              return_total_rows=False,
              sort_attr=None, sort_asc=True):
        """
        Perform a query in a database
        And operator is &&
        Example prepid=*19*&&is_root=false
        This is horrible, please think of something better
        """
        query_dict = {}
        if query_string:
            query_dict = {'$and': []}
            query_string_parts = [x.strip() for x in query_string.split('&&') if x.strip()]
            self.logger.info('Query parts %s', query_string_parts)
            for part in query_string_parts:
                split_part = part.split('=')
                key = split_part[0]
                value = split_part[1].replace('*', '.*')
                value_condition = None
                if '<' in value[0]:
                    value_condition = '$lt'
                    value = value[1:]
                elif value[0] == '>':
                    value_condition = '$gt'
                    value = value[1:]
                elif value[0] == '!':
                    value_condition = '$ne'
                    value = value[1:]

                if '<int>' in key:
                    value = int(value)
                    if value_condition:
                        value = {value_condition: value}

                    query_dict['$and'].append({key.replace('<int>', ''): value})
                elif '<float>' in key:
                    value = float(value)
                    if value_condition:
                        value = {value_condition: value}

                    query_dict['$and'].append({key.replace('<float>', ''): value})
                else:
                    if value_condition:
                        value = {value_condition: value}
                        query_dict['$and'].append({key: value})
                    elif '*' in value:
                        query_dict['$and'].append({key: {'$regex': value}})
                    else:
                        query_dict['$and'].append({key: value})

        self.logger.debug('Database "%s" query dict %s', self.database_name, query_dict)
        result = self.database.find(query_dict)
        if not sort_attr:
            sort_attr = '_id'

        result = result.sort(sort_attr, 1 if sort_asc else -1)
        total_rows = result.count()
        result = result.skip(page * limit).limit(limit)
        if return_total_rows:
            return list(result), int(total_rows)

        return list(result)

    def build_query_with_types(self, query_string, object_class):
        """
        This is horrible, please think of something better
        """
        schema = object_class.schema()
        query_string_parts = [x.strip() for x in query_string.split('&&') if x.strip()]
        typed_arguments = []
        for part in query_string_parts:
            split_part = part.split('=')
            key = split_part[0]
            value = split_part[1]
            if key in Database.__SEARCH_RENAME.get(self.database_name, {}):
                key = Database.__SEARCH_RENAME[self.database_name][key]
            elif isinstance(schema.get(key), (int, float)):
                key = f'{key}<{type(schema.get(key)).__name__}>'

            typed_arguments.append(f'{key}={value}')

        return '&&'.join(typed_arguments)
