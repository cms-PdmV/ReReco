from core.database.database import Database
from core.model.model_base import ModelBase
from core.utils.locker import Locker


class ControllerBase():
    """
    Controller base class implements simple create, read, update, delete methods
    as well as some convenience methods such as get_changed_values for update
    This is a base class for all controllers
    It requires database name and class object of model
    """

    def __init__(self):
        self.logger = ModelBase._ModelBase__logger
        self.locker = Locker()
        self.database_name = None
        self.model_class = None

    def create(self, json_data):
        """
        Create a new object from given json_data
        """
        new_object = self.model_class(json_input=json_data)
        prepid = new_object.get_prepid()

        database = Database(self.database_name)
        if database.get(prepid):
            raise Exception(f'Object with prepid "{prepid}" already exists in {self.database_name} database')

        with self.locker.get_lock(prepid):
            self.logger.info('Will create %s', (prepid))
            new_object.add_history('create', prepid, None)
            if self.check_for_create(new_object):
                database.save(new_object.json())
                return new_object.json()
            else:
                self.logger.error('Error while checking new item %s', prepid)
                return None

    def get(self, prepid):
        """
        Return a single object if it exists in database
        """
        database = Database(self.database_name)
        object_json = database.get(prepid)
        if object_json:
            return self.model_class(json_input=object_json)
        else:
            return None

    def update(self, json_data):
        """
        Update a single object with given json
        """
        new_object = self.model_class(json_input=json_data)
        prepid = new_object.get_prepid()
        with self.locker.get_lock(prepid):
            self.logger.info('Will edit %s', prepid)
            database = Database(self.database_name)
            old_object = database.get(prepid)
            if not old_object:
                raise Exception(f'Object with prepid "{prepid}" does not exist in {self.database_name} database')

            old_object = self.model_class(json_input=old_object)
            # Move over history, so it could not be overwritten
            new_object.set('history', old_object.get('history'))
            changed_values = self.get_changed_values(old_object, new_object)
            if not changed_values:
                # Nothing was updated
                self.logger.info('Nothing was updated for %s', prepid)
                return old_object.json()

            new_object.add_history('update', changed_values, None)
            if self.check_for_update(old_object, new_object, changed_values):
                database.save(new_object.json())
                return new_object.json()
            else:
                self.logger.error('Error while updating %s', prepid)
                return None

    def delete(self, json_data):
        """
        Delete a single object
        """
        obj = self.model_class(json_input=json_data)
        prepid = obj.get_prepid()

        database = Database(self.database_name)
        if not database.get(prepid):
            raise Exception(f'Object with prepid "{prepid}" does not exist in {self.database_name} database')

        with self.locker.get_lock(prepid):
            self.logger.info('Will delete %s', (prepid))
            if self.check_for_delete(obj):
                database.delete_document(obj.json())
                return {'prepid': prepid}
            else:
                self.logger.error('Error while deleting %s', prepid)
                return None

    def check_for_create(self, obj):
        """
        Perform checks on object before adding it to database
        """
        raise NotImplementedError('This method must be implemented')

    def check_for_update(self, old_obj, new_obj):
        """
        Compare existing and updated objects to see if update is valid
        """
        raise NotImplementedError('This method must be implemented')

    def check_for_delete(self, obj):
        """
        Perform checks on object before deleting it from database
        """
        raise NotImplementedError('This method must be implemented')

    def get_changed_values(self, reference, target, prefix=None, changed_values=None):
        """
        Get dictionary of different values across two objects
        """
        if changed_values is None:
            changed_values = []

        if prefix is None:
            prefix = ''

        if isinstance(reference, ModelBase) and isinstance(reference, ModelBase):
            # Comparing two ReReco objects
            schema = reference.schema()
            schema_keys = schema.keys()
            for key in schema_keys:
                self.get_changed_values(reference.get(key),
                                        target.get(key),
                                        '%s.%s' % (prefix, key),
                                        changed_values)

        elif isinstance(reference, dict) and isinstance(target, dict):
            # Comparing two dictionaries
            keys = reference.keys()
            for key in keys:
                self.get_changed_values(reference.get(key),
                                        target.get(key),
                                        '%s.%s' % (prefix, key),
                                        changed_values)
        elif isinstance(reference, list) and isinstance(target, list):
            # Comparing two lists
            if len(reference) != len(target):
                changed_values.append(prefix.lstrip('.').lstrip('_'))
            else:
                for i in range(min(len(reference), len(target))):
                    self.get_changed_values(reference[i],
                                            target[i],
                                            '%s_%s' % (prefix, i),
                                            changed_values)
        else:
            # Comparing two values
            if reference != target:
                changed_values.append(prefix.lstrip('.').lstrip('_'))

        return changed_values
