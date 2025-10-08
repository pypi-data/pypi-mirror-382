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

class UploadApi(object):
    def __init__(self, configuration=None):
        self.configuration = configuration
        host = self.configuration.host.replace('https://', '')

        self.http = urllib3.HTTPSConnectionPool(host, port=443, cert_reqs='CERT_NONE',
                                                assert_hostname=False, timeout=Timeout(connect=2.0, read=10.0))

    def upload(self, dataset_id: str, file_config: object):
        """This method will upload a file to KDP

            :param str dataset_id: ID of dataset that file will be uploaded to
            :param object file_config: JSON containing filename and path ex. { "filename": "test.csv", "path": "/path/to/file" }
                   optional properties of file_config:
                    { ... "accessControlLabel": accessControlLabelJsonObject, "customMetadata": customMetadataJsonObject }

                   see API documentation for uploads: https://documentation.koverse.com/api/#tag/uploads/operation/post_uploads

        """
        fields = {
            'datasetId': dataset_id,
            'files': (file_config['filename'], open(file_config['path'], 'rb').read()),
        }

        if 'processAsDocument' in file_config:
            fields['processAsDocument'] = file_config['processAsDocument']

        if 'accessControlLabel' in file_config:
            fields['accessControlLabel'] = file_config['accessControlLabel']

        if 'customMetadata' in file_config:
            fields['customMetadata'] = file_config['customMetadata']

        response = self.http.request(
            'POST',
            self.configuration.host + '/uploads',
            headers={
                'Authorization': 'Bearer ' + self.configuration.access_token
            },
            fields=fields
        )

        return response
