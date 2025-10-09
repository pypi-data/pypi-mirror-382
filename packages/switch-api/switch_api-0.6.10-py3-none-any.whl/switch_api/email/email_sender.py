# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for sending emails with attachments to active users within a portfolio in the Switch Automation Platform.
"""

import logging
import sys
from typing import Union
import requests
import mimetypes
import os
from .._utils._utils import ApiInputs

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)


def send_email(
        api_inputs: ApiInputs, body: str, subject: str,
        to_recipients: list[str], cc_recipients: list[str] = [], bcc_recipients: list[str] = [],
        attachments: list[str] = [], attachments_mime_types: list[str] = [], conversation_id: Union[str, None] = None):
    """
    Sends an email with attachments to the specified active users within a portfolio in the Switch Automation Platform.

    Parameters
    ----------
    api_inputs : ApiInputs
        The API Inputs object.
    body : str
        The body of the email.
    subject : str
        The subject of the email.
    to_recipients : list[str]
        The list of recipient emails.
    cc_recipients : list[str], optional
        The list of cc recipient emails, by default None.
    bcc_recipients : list[str], optional
        The list of bcc recipient emails, by default None.
    attachments : list[str], optional
        The list of attachment paths, by default None.
    attachments_mime_types : list[str], optional
        The list of attachment mime types, by default None.
        Use this parameter to specify the mime type of the attachments that are being guessed incorrectly.
        Ensure length and order of this list matches the attachments list.
        Provide None for the attachments that are being guessed correctly.
    conversation_id : str, optional
        Correlate related emails into a thread by specifying the same conversation id, by default None.

    Returns
    -------
    bool
        True if the email was sent successfully, False otherwise.

    Examples
    --------
    >>> import switch_api as sw
    >>> api_inputs = sw.initialize(api_project_id='<project_id>')
    >>> body = "<div>Sending attachments</div>"
    >>> subject = 'Test Email with Attachments'
    >>> to_recipients = ["email@example.com"]
    >>> # Optional attachments
    >>> attachments = [
        'Path/To/Attachment/File.<ext>',
        'Path/To/Attachment/File2.<ext>'
    ]
    >>> send_email(api_inputs=api_inputs, body=body, subject=subject, to_recipients=to_recipients, attachments=attachments)
    """

    if not body:
        logger.error("No body was provided")
        return False

    if not subject:
        logger.error("No subject was provided")
        return False

    if to_recipients is None or len(to_recipients) == 0:
        logger.error("No recipients were provided")
        return False

    logger.info(f'Sending email to recipients: {to_recipients}')

    url = f"{api_inputs.api_projects_endpoint}/{api_inputs.api_project_id}/task-insights/email/send"

    data = {
        "Subject": subject,
        "ContentHtml": body
    }

    if conversation_id:
        data["ConversationId"] = conversation_id

    for index, email in enumerate(to_recipients):
        data[f"ToRecipients[{index}]"] = email

    for index, email in enumerate(cc_recipients or []):
        data[f"CcRecipients[{index}]"] = email

    for index, email in enumerate(bcc_recipients or []):
        data[f"BccRecipients[{index}]"] = email

    files = []
    for index, attachmentPath in enumerate(attachments or []):
        filename = os.path.basename(attachmentPath)
        mimetype = attachments_mime_types[index] \
            if attachments_mime_types and len(attachments_mime_types) >= index \
            else mimetypes.guess_type(filename)[0]

        files.append(
            ('Attachments', (filename, open(attachmentPath, 'rb'), mimetype))
        )

    headers = api_inputs.api_headers.default.copy()
    del headers['Content-Type']

    logger.info("Sending request: POST %s", url)
    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        logger.error(f"API Call was not successful. Response Status: {response.status_code}. Reason: {response.reason}. "
                     f"Response: {response.text}")
        return False

    logger.info(response.text)
    return True
