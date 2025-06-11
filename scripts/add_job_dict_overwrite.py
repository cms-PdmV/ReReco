import sys
import os.path
import os
# pylint: disable-next=wrong-import-position
sys.path.append(os.path.abspath(os.path.pardir))
from core_lib.database.database import Database

Database.set_credentials_file(os.getenv('DB_AUTH'))
Database.set_database_name('rereco')

database = Database('tickets')

total_entries = database.get_count()

print('Total entries: %s' % (total_entries))

for index, item in enumerate(database.query(limit=total_entries)):
    print('Processing entry %s/%s %s' % (index + 1, total_entries, item.get('prepid', '<no-id>')))
    item['job_dict_overwrite'] = {}
    database.save(item)

print('Done')
