# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module for .....
"""
import json
import logging
import sys
from multiprocessing import Process
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .._utils._utils import ApiInputs
import uvicorn
from .processor import RequestProcessor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  switch_api.%(module)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)

def local_start(api_inputs: ApiInputs, script_path: str):
    """Starts a local Guides Engine that allows processing and debugging
    of tasks locally.

    Args:
        api_inputs (ApiInputs): Provides state for calling Switch Platform APIs.
        script_path (str): Local file path of the Python Script / Task for processing / debugging
    """
    args = (script_path, api_inputs)

    process = Process(target=_server_run, args=args)
    process.start()


def _server_run(script_path, api_inputs):

    app = FastAPI()
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/guides/functions/execute")
    async def functions_execute(request: Request):
        data_bytes = await request.body()
        data_str = data_bytes.decode('utf-8')

        if not data_str:
            # # logger.error('No data in event')
            return {'success': True}

        data: dict = json.loads(data_str)

        if data is None or len(data) == 0:
            # # logger.error('No data in event')
            return {'success': True}

        # We have some cases where the payload body is in lowercase and in uppercase, to be flexible we handle it in this side of the engine - change all to lowercase
        data = _keys_to_lowercase(data)

        try:
            message_processor = RequestProcessor(
                api_inputs=api_inputs, script_path=script_path, data=data)

            result = message_processor.process()
            logger.info(result)

            if not result:
                return {'success': True}
            else:
                return result
        except Exception as e:
            return {'success': False}

    uvicorn.run(app, host='0.0.0.0', port=int(8000))


def _keys_to_lowercase(input_dict):
    lowercase_dict = {}
    for key, value in input_dict.items():
        lowercase_key = key.lower()  # Convert the key to lowercase
        lowercase_dict[lowercase_key] = value
    return lowercase_dict
