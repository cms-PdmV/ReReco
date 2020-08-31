"""
Module that contains all search APIs
"""
import re
import flask
from core_lib.api.api_base import APIBase
from core_lib.database.database import Database
from core.model.subcampaign import Subcampaign
from core.model.ticket import Ticket
from core.model.request import Request


class SearchAPI(APIBase):
    """
    Endpoint that is used for search in the database
    """

    def __init__(self):
        APIBase.__init__(self)
        self.classes = {'subcampaigns': Subcampaign,
                        'requests': Request,
                        'tickets': Ticket}

    @APIBase.exceptions_to_errors
    def get(self):
        """
        Perform a search
        """
        args = flask.request.args.to_dict()
        if args is None:
            args = {}

        db_name = args.get('db_name', None)
        page = int(args.get('page', 0))
        limit = int(args.get('limit', 20))

        if 'db_name' in args:
            del args['db_name']

        if 'page' in args:
            del args['page']

        if 'limit' in args:
            del args['limit']

        # Special cases
        from_ticket = args.pop('ticket', None)
        if db_name == 'requests' and from_ticket:
            ticket_database = Database('tickets')
            ticket = ticket_database.get(from_ticket)
            created_requests = ','.join(ticket['created_requests'])
            prepid_query = args.pop('prepid', '')
            args['prepid'] = ('%s,%s' % (prepid_query, created_requests)).strip(',')

        query_string = '&&'.join(['%s=%s' % (pair) for pair in args.items()])
        database = Database(db_name)
        query_string = database.build_query_with_types(query_string, self.classes[db_name])
        results, total_rows = database.query_with_total_rows(query_string, page, limit)

        return self.output_text({'response': {'results': results,
                                              'total_rows': total_rows},
                                 'success': True,
                                 'message': ''})

class SuggestionsAPI(APIBase):
    """
    Endpoint that is used to fetch suggestions
    """

    def __init__(self):
        APIBase.__init__(self)

    @APIBase.exceptions_to_errors
    def get(self):
        """
        Return a list of prepid suggestions for given query
        """
        args = flask.request.args.to_dict()
        if args is None:
            args = {}

        db_name = args.pop('db_name', None)
        query = args.pop('query', None).replace(' ', '.*')
        limit = max(1, min(50, args.pop('limit', 20)))

        if not db_name or not query:
            raise Exception('Bad db_name or query parameter')

        database = Database(db_name)
        db_query = {'prepid': re.compile(f'.*{query}.*', re.IGNORECASE)}
        results = database.collection.find(db_query).limit(limit)
        results = [x['prepid'] for x in results]

        return self.output_text({'response': results,
                                 'success': True,
                                 'message': ''})
