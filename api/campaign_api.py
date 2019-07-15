"""
Module that contains all campaign APIs
"""
import json
import flask
from api.api_base import APIBase
from core.controller.campaign_controller import CampaignController


campaign_controller = CampaignController()


class CreateCampaignAPI(APIBase):

    def __init__(self):
        APIBase.__init__(self)

    @APIBase.ensure_request_data
    @APIBase.exceptions_to_errors
    def put(self):
        """
        Create a campaign with the provided JSON content. Requires a unique prepid
        """
        data = flask.request.data
        campaign_json = json.loads(data.decode('utf-8'))
        prepid = campaign_controller.create_campaign(campaign_json)
        return self.output_text({'response': prepid, 'success': True, 'message': ''})


class DeleteCampaignAPI(APIBase):

    def __init__(self):
        APIBase.__init__(self)

    @APIBase.ensure_request_data
    @APIBase.exceptions_to_errors
    def delete(self):
        """
        Delete a campaign with the provided JSON content
        """
        data = flask.request.data
        campaign_json = json.loads(data.decode('utf-8'))
        prepid = campaign_controller.delete_campaign(campaign_json)
        return self.output_text({'response': prepid, 'success': True, 'message': ''})


class UpdateCampaignAPI(APIBase):

    def __init__(self):
        APIBase.__init__(self)

    @APIBase.ensure_request_data
    @APIBase.exceptions_to_errors
    def post(self):
        """
        Update a campaign with the provided JSON content
        """
        data = flask.request.data
        campaign_json = json.loads(data.decode('utf-8'))
        prepid = campaign_controller.update_campaign(campaign_json)
        return self.output_text({'response': prepid, 'success': True, 'message': ''})


class GetCampaignAPI(APIBase):

    def __init__(self):
        APIBase.__init__(self)

    @APIBase.exceptions_to_errors
    def get(self, prepid):
        """
        Get a single campaign with given prepid
        """
        campaign = campaign_controller.get_campaign(prepid)
        return self.output_text({'response': campaign.json(), 'success': True, 'message': ''})
