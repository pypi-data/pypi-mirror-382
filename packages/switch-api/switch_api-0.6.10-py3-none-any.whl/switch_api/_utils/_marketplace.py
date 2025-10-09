# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
import logging
import os
import sys
import uuid
import pandas
import requests
from .._utils._utils import ApiInputs, _column_name_cap
from .._utils._constants import GUIDES_EXTERNAL_TYPES, GUIDES_SCOPE

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def add_marketplace_item(api_inputs: ApiInputs, name: str, short_description: str, description: str,
                         tags: dict, external_id: uuid.UUID, card_image_file_name: str = '',
                         external_type: GUIDES_EXTERNAL_TYPES = 'SwitchGuides', scope: GUIDES_SCOPE = 'Portfolio-wide',
                         image_file_name: str = '', version: str = ''):
    """Add datafeed driver to Marketplace Items

    Parameters
    ----------
    api_inputs : ApiInputs
        Provides state for calling Switch Platform APIs.
    name : str
        Name of the Task when added to the Marketplace Items
    short_description : str
        Short description for the Marketplace Item registration. Max 250 characters.
    description : str
        Full description for the Marketplace Item registration
    tags : dict
        Tags for Marketplace item registration. Required atleast 1 tag
    external_id : uuid.UUID
        The Marketplace ID (defined on the task).
    card_image_file_name : str, optional
        Card Image File Name for Marketplace Items. Defaults to ''.
    external_type : GUIDES_EXTERNAL_TYPES, optional
        Marketplaec External Type. Defaults to 'SwitchGuides'.
    scope : GUIDES_SCOPE, optional
        Marketplace item scope. Defaults to 'Portfolio-wide'.
    image_file_name : str, optional
        For Marketplace item image. Defaults to ''.
    version : str, optional
        For Marketplace item versioning. Defaults to ''.

    Returns
    -------
    pandas.Dataframe
    """

    if api_inputs.api_base_url == '' or api_inputs.bearer_token == '':
        logger.error("You must call initialize() before using API.")
        return pandas.DataFrame()

    if not name.strip():
        logger.exception("The name property cannot be empty.")
        raise Exception("The name property cannot be empty.")
    if not description.strip():
        logger.exception("The description property cannot be empty.")
        raise Exception("The description property cannot be empty.")
    if not short_description.strip():
        logger.exception("The short_description property cannot be empty.")
        raise Exception("The short_description property cannot be empty.")
    if type(tags) != dict:
        logger.exception("The tags property must be a dictionary with at least one key. ")
        raise Exception("The tags property must be a dictionary with at least one key. ")
    if len(tags.keys()) < 1:
        logger.exception("The tags property must be a dictionary with at least one key. ")
        raise Exception("The tags property must be a dictionary with at least one key. ")

    if type(image_file_name) != str:
        logger.exception("The image_file_name property must be a string. ")
        raise Exception("The image_file_name property must be a string. ")
    if type(card_image_file_name) != str:
        logger.exception("The card_image_file_name property be a string. ")
        raise Exception("The card_image_file_name property must be a string. ")

    headers = api_inputs.api_headers.default

    # enforce these values
    scope = 'Portfolio-wide'
    external_type = 'SwitchGuides'
    container_name = 'guides-form'

    if not version.strip():
        version = '0.1.0'

    image_url = f'{image_file_name}'
    card_image_url = f'{card_image_file_name}'

    payload = {
        "name": name,
        "shortDescription": short_description,
        "description": description,
        "version": version,
        "externalType": external_type,
        "externalId": external_id,
        "tags": tags,
        "scope": scope,
        "imageUrl": image_url,
        "cardImageUrl": card_image_url
    }

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/guide/register"

    logger.info("Sending request: POST %s", url)

    response = requests.post(url, json=payload, headers=headers)
    response_status = '{} {}'.format(response.status_code, response.reason)

    if response.status_code != 200 and len(response.text) > 0:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        error_df = pandas.read_json(response.text)
        return response_status, error_df
    elif response.status_code != 200 and len(response.text) == 0:
        logger.error("API Call was not successful. Response Status: %s. Reason: %s.", response.status_code,
                     response.reason)
        return response_status, pandas.DataFrame()
    elif len(response.text) == 0:
        logger.error('No data returned for this API call. %s',
                     response.request.url)
        return response_status, pandas.DataFrame()

    if (response.text == '[]'):
        logger.info('No changes with the records from Marketplace.')
        df = pandas.DataFrame()
    else:
        df = pandas.read_json(response.text, typ='Series').to_frame().T
        df.columns = _column_name_cap(df.columns)

    return df
