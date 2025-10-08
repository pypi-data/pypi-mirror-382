import kdp_api
from kdp_api.api import manage_records_api
from kdp_api.models.job import Job

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

class StorageApi(object):

    def clear_dataset(self, config, dataset_id: str) -> Job:
        """This method will be used to clear dataset.

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will queried

            :returns: clear dataset job

            :rtype: Job
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = manage_records_api.ManageRecordsApi(api_client)
            return api_instance.post_clear_dataset(dataset_id=dataset_id)
