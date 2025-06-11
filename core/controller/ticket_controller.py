"""
Module that contains TicketController class
"""
from core_lib.utils.settings import Settings
from core_lib.database.database import Database
from core_lib.controller.controller_base import ControllerBase
from core_lib.utils.common_utils import dbs_datasetlist
from core.model.model_base import ModelBase
from core.model.ticket import Ticket
from core.controller.request_controller import RequestController


class TicketController(ControllerBase):
    """
    Controller that has all actions related to a ticket
    """

    def __init__(self):
        ControllerBase.__init__(self)
        self.database_name = 'tickets'
        self.model_class = Ticket

    def create(self, json_data):
        # Clean up the input
        ticket_db = Database(self.database_name)
        json_data['prepid'] = 'Temp00001'
        ticket = Ticket(json_input=json_data)
        # Use first subcampaign name for prepid
        subcampaign_name = ticket.get('steps')[0]['subcampaign']
        processing_string = ticket.get('steps')[0]['processing_string']
        prepid_middle_part = f'{subcampaign_name}-{processing_string}'
        with self.locker.get_lock(f'create-subcampaign-ticket-prepid-{prepid_middle_part}'):
            # Get a new serial number
            serial_number = self.get_highest_serial_number(ticket_db,
                                                           f'{prepid_middle_part}-*')
            serial_number += 1
            # Form a new temporary prepid
            prepid = f'{prepid_middle_part}-{serial_number:05d}'
            json_data['prepid'] = prepid
            new_ticket_json = super().create(json_data)

        return new_ticket_json

    def check_input(self, ticket):
        """
        Check ticket's input, if all datasets and requests exist and are not
        blacklisted
        """
        ticket_input = ticket.get('input')
        duplicates = list(set(x for x in ticket_input if ticket_input.count(x) > 1))
        if duplicates:
            raise ValueError(f'Duplicates in input: {", ".join(duplicates)}')

        dataset_blacklist = set(Settings().get('dataset_blacklist'))
        request_controller = RequestController()
        datasets = []
        for input_item in ticket_input:
            if ModelBase.dataset_check(input_item):
                datasets.append(input_item)
                dataset = input_item.split('/')[1]

            elif ModelBase.request_id_check(input_item):
                request = request_controller.get(input_item)
                dataset = request.get_dataset()

            if dataset in dataset_blacklist:
                raise AssertionError(f'Input dataset {input_item} is not '
                                     f'allowed because {dataset} is in blacklist')

        dataset_info = {x['dataset']: x['dataset_access_type'] for x in dbs_datasetlist(datasets)}
        self.logger.info(dataset_info)
        for dataset in datasets:
            dataset_status = dataset_info.get(dataset, 'NONE')
            if dataset_status not in {'VALID', 'PRODUCTION'}:
                raise AssertionError(
                    (
                        f'Input dataset {dataset} status is {dataset_status} or it could '
                        'not be found. Required status is either VALID or PRODUCTION'
                    )
                )

    def check_steps(self, ticket):
        """
        Check ticket's steps: whether subcampaign exists and step has correct
        number of time per event and size per event values
        """
        subcampaign_database = Database('subcampaigns')
        for index, step in enumerate(ticket.get('steps')):
            subcampaign_name = step['subcampaign']
            subcampaign = subcampaign_database.get(subcampaign_name)
            if not subcampaign:
                raise ValueError(f'Subcampaign {subcampaign_name} does not exist')

            subcampaign_sequences = subcampaign['sequences']
            time_per_event = step['time_per_event']
            size_per_event = step['size_per_event']
            if len(time_per_event) != len(subcampaign_sequences):
                raise AssertionError(f'Step {index + 1} has {len(time_per_event)} time per '
                                     f'event values, expected {len(subcampaign_sequences)}')

            if len(size_per_event) != len(subcampaign_sequences):
                raise AssertionError(f'Step {index + 1} has {len(size_per_event)} size per '
                                     f'event values, expected {len(subcampaign_sequences)}')

    def check_for_create(self, obj):
        self.check_input(obj)
        self.check_steps(obj)
        return True

    def check_for_update(self, old_obj, new_obj, changed_values):
        self.check_input(new_obj)
        self.check_steps(new_obj)
        return True

    def check_for_delete(self, obj):
        created_requests = obj.get('created_requests')
        prepid = obj.get('prepid')
        if created_requests:
            raise AssertionError(f'It is not allowed to delete tickets that have requests created. '
                                 f'{prepid} has {len(created_requests)} requests')

        return True

    def get_datasets(self, query, exclude_list=None):
        """
        Query DBS for list of datasets
        """
        with self.locker.get_lock('get-ticket-datasets'):
            datasets = dbs_datasetlist(query)

        if not datasets:
            return []

        valid_types = {'VALID', 'PRODUCTION'}
        datasets = [x['dataset'] for x in datasets if x['dataset_access_type'] in valid_types]
        dataset_blacklist = set(Settings().get('dataset_blacklist'))
        datasets = [x for x in datasets if x.split('/')[1] not in dataset_blacklist]
        if exclude_list:
            filtered_datasets = []
            for dataset in datasets:
                for exclude in exclude_list:
                    if exclude in dataset:
                        break
                else:
                    filtered_datasets.append(dataset)

            datasets = filtered_datasets

        self.logger.info('Got %s datasets from DBS for query %s', len(datasets), query)
        return datasets

    def get_requests(self, query):
        """
        Query database for list of requests
        """
        requests_db = Database('requests')
        requests = requests_db.query(f'prepid={query}', limit=1000)
        requests = [x['prepid'] for x in requests]
        self.logger.info('Got %s requests from database for query %s', len(requests), query)
        return requests

    def get_editing_info(self, obj):
        editing_info = super().get_editing_info(obj)
        status = obj.get('status')
        editing_info['notes'] = True
        editing_info['steps'] = []
        not_done = status != 'done'
        editing_info['input'] = not_done
        editing_info['__steps'] = not_done
        editing_info['job_dict_overwrite'] = not_done
        for step_index, _ in enumerate(obj.get('steps')):
            editing_info['steps'].append({'subcampaign': step_index > 0 and not_done,
                                          'processing_string': step_index > 0 and not_done,
                                          'size_per_event': not_done,
                                          'time_per_event': not_done,
                                          'priority': not_done})

        return editing_info

    def create_requests_for_ticket(self, ticket):
        """
        Create requests from given ticket. Return list of request prepids
        """
        database = Database(self.database_name)
        ticket_prepid = ticket.get_prepid()
        created_requests = []
        request_controller = RequestController()
        ticket_job_overwrite = ticket.get('job_dict_overwrite')
        with self.locker.get_lock(ticket_prepid):
            ticket = Ticket(json_input=database.get(ticket_prepid))
            created_requests = ticket.get('created_requests')
            status = ticket.get('status')
            if status != 'new':
                raise AssertionError(f'Ticket is not new, it already has '
                                     f'{len(created_requests)} requests created')

            # In case black list was updated after ticket was created
            self.check_input(ticket)
            self.check_steps(ticket)
            try:
                for input_item in ticket.get('input'):
                    last_request_prepid = None
                    for step_index, step in enumerate(ticket.get('steps')):
                        subcampaign_name = step['subcampaign']
                        new_request_json = {'subcampaign': subcampaign_name,
                                            'job_dict_overwrite': ticket_job_overwrite,
                                            'priority': step['priority'],
                                            'processing_string': step['processing_string'],
                                            'time_per_event': step['time_per_event'],
                                            'size_per_event': step['size_per_event'],
                                            'input': {'dataset': '',
                                                      'request': ''}}

                        if step_index == 0:
                            if ModelBase.dataset_check(input_item):
                                new_request_json['input']['dataset'] = input_item
                            elif ModelBase.request_id_check(input_item):
                                new_request_json['input']['request'] = input_item
                        else:
                            new_request_json['input']['request'] = last_request_prepid

                        try:
                            runs = request_controller.get_runs(subcampaign_name, input_item)
                            new_request_json['runs'] = runs
                            lumis = request_controller.get_lumisections(subcampaign_name, runs)
                            new_request_json['lumisections'] = lumis
                        except Exception as ex:
                            self.logger.error('Error getting runs or lumis for %s %s: \n%s',
                                              subcampaign_name,
                                              input_item,
                                              ex)

                        request = request_controller.create(new_request_json)
                        created_requests.append(request)
                        last_request_prepid = request.get('prepid')
                        self.logger.info('Created %s', last_request_prepid)

                created_request_prepids = [r.get('prepid') for r in created_requests]
                ticket.set('created_requests', created_request_prepids)
                ticket.set('status', 'done')
                ticket.add_history('create_requests', created_request_prepids, None)
                database.save(ticket.get_json())
            except Exception as ex:
                # Delete created requests if there was an Exception
                for created_request in reversed(created_requests):
                    request_controller.delete({'prepid': created_request.get('prepid')})

                # And reraise the exception
                raise ex

        return [r.get('prepid') for r in created_requests]

    def get_twiki_snippet(self, ticket):
        """
        Generate tables for TWiki
        Requests are grouped by acquisition eras in input datasets
        """
        prepid = ticket.get_prepid()
        self.logger.debug('Returning TWiki snippet for %s', prepid)
        acquisition_eras = {}
        request_controller = RequestController()
        for request_prepid in ticket.get('created_requests'):
            request = request_controller.get(request_prepid)
            acquisition_era = request.get_era()
            acquisition_eras.setdefault(acquisition_era, []).append(request)

        output_strings = []
        pmp_url = 'https://cms-pdmv-prod.web.cern.ch/pmp/historical?r='
        for acquisition_era in sorted(acquisition_eras.keys()):
            requests = acquisition_eras[acquisition_era]
            output_strings.append(f'---+++ !{acquisition_era}\n')
            output_strings.append('| *Dataset* | *Monitoring link* | *Runs* |')
            for request in requests:
                prepid = request.get_prepid()
                runs = request.get('runs')
                runs = ', '.join(str(r) for r in runs)
                dataset = request.get_dataset()
                output_strings.append(f'| {dataset} | [[{pmp_url}{prepid}][{prepid}]] | {runs} |')

            output_strings.append('\n')

        return '\n'.join(output_strings).strip()
