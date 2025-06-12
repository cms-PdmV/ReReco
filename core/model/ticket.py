"""
Module that contains Ticket class
"""
from copy import deepcopy
from core.model.model_base import ModelBase


class Ticket(ModelBase):
    """
    Ticket has a list of input datasets and a list of steps specifications
    Ticket is used to create requests for each input dataset
    """

    _ModelBase__schema = {
        # Database id (required by DB)
        '_id': '',
        # PrepID
        'prepid': '',
        # List of prepids of requests that were created from this ticket
        'created_requests': [],
        # Action history
        'history': [],
        # List of input dataset names or request prepids
        'input': [],
        # User notes
        'notes': '',
        # Status is either new or done
        'status': 'new',
        # List of dicts that have subcampaign, processing_string, size/time per event values
        'steps': [],
        # Manual overwrite of job dictionary for the request to be created
        # a default template for them
        'job_dict_overwrite': {},
    }

    lambda_checks = {
        'prepid': ModelBase.ticket_id_check,
        '__created_requests': ModelBase.request_id_check,
        '__input': lambda i: ModelBase.dataset_check(i) or ModelBase.request_id_check(i),
        'status': lambda status: status in {'new', 'done'},
        'steps': lambda s: len(s) > 0,
    }

    def __init__(self, json_input=None, check_attributes=True):
        if json_input:
            json_input = deepcopy(json_input)
            steps = []
            for step in json_input.get('steps', []):
                steps.append({'subcampaign': step.get('subcampaign', ''),
                              'processing_string': step.get('processing_string', ''),
                              'time_per_event': [float(t) for t in step.get('time_per_event', 0)],
                              'size_per_event': [float(s) for s in step.get('size_per_event', 0)],
                              'priority': int(step.get('priority', 0))})

            json_input['steps'] = steps

        ModelBase.__init__(self, json_input, check_attributes)

    def check_attribute(self, attribute_name, attribute_value):
        if attribute_name == 'steps':
            if not isinstance(attribute_value, list):
                raise TypeError(f'Expected {attribute_name} to be a list')

            for step in attribute_value:
                subcampaign = step['subcampaign']
                if not ModelBase.lambda_check('subcampaign')(subcampaign):
                    raise ValueError(f'Bad subcampaign prepid {subcampaign}')

                processing_string = step['processing_string']
                if not ModelBase.lambda_check('processing_string')(processing_string):
                    raise ValueError(f'Bad processing string {processing_string}')

                time_per_event = step['time_per_event']
                if [t for t in time_per_event if t <= 0.0]:
                    raise ValueError('Time per event must be > 0')

                size_per_event = step['size_per_event']
                if [s for s in size_per_event if s <= 0.0]:
                    raise ValueError('Size per event must be > 0')

                priority = step['priority']
                if not ModelBase.lambda_check('priority')(priority):
                    raise ValueError(f'Bad priority {priority}')

        return super().check_attribute(attribute_name, attribute_value)
