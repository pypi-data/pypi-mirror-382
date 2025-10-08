import json
import logging

import urllib3
from urllib3.util import Timeout

# Copyright 2025 SAIC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class IngestJobApi(object):
    def __init__(self, configuration=None):
        self.configuration = configuration
        host = self.configuration.host.replace('https://', '')

        self.http = urllib3.HTTPSConnectionPool(host, port=443, cert_reqs='CERT_NONE',
                                                assert_hostname=False, timeout=Timeout(connect=2.0, read=10.0))

    def create_url_ingest_job(self, workspace_id: str, dataset_id: str, url_list) -> str:

        """This method will be used to start a job that ingests files to KDP

            :param str workspace_id: ID of KDP workspace data will be written to
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param list url_list: List of urls for each file to be ingested

            :returns: Job ID

            :rtype: str
        """

        ingest_request = {}
        ingest_request['workspaceId'] = workspace_id
        ingest_request['datasetId'] = dataset_id
        ingest_request['securityLabeled'] = False
        ingest_request['dataSourceParams'] = {}
        ingest_request['dataSourceParams']['type'] = 'URL'
        ingest_request['dataSourceParams']['connectionInfo'] = {}
        ingest_request['dataSourceParams']['connectionInfo']['urls'] = []

        for url_str in url_list:
            url = {}
            url['url'] = url_str
            ingest_request['dataSourceParams']['connectionInfo']['urls'].append(url)

        return self.create_ingest_job(ingest_request)

    def create_ingest_job(self, ingest_request: object) -> str:
        encoded_data = json.dumps(ingest_request).encode('utf-8')

        if self.configuration.access_token is None and self.configuration.api_key is not None:
            api_key_value = self.configuration.api_key['APIKey']
            result: urllib3.response.HTTPResponse = self.http.request(
                'POST',
                self.configuration.host + "/ingest",
                body=encoded_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': api_key_value
                }
            )
        else:
            result: urllib3.response.HTTPResponse = self.http.request(
                'POST',
                self.configuration.host + "/ingest",
                body=encoded_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.configuration.access_token
                }
            )

        if result.status == 202:
            return json.loads(result.data)
        else:
            logging.error('unexpected response code returned. status: %s, reason: %s, message: %s' %
                          (result.status, result.reason, result.msg))
            raise Exception('Failed to create ingest job')
