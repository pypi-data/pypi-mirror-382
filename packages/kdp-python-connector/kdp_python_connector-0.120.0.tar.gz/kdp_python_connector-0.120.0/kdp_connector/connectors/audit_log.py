import logging

import kdp_api
from kdp_api import LuceneQueryRequest
from kdp_api.api import workspaces_api
from kdp_api.configuration import Configuration
from kdp_api.models.audit_log_paginator import AuditLogPaginator

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

class AuditLogApi(object):
    def __init__(self, configuration: Configuration=None):
        self.configuration = configuration


    def post_audit_log_query(self, config, dataset_id: str, expression: str, limit: int = 5, offset: int = 0) -> AuditLogPaginator:
        """This method will be used to query data in KDP datasets using the lucene syntax

            :param Configuration config: Connection configuration
            :param str dataset_id: audit log dataset id
            :param str expression: Lucene style query expression ex. name: John
            :param int limit: max number of results in the response.
            :param int offset: how many records to skip before returning first record.
            :returns: AuditLogPaginator object which contains audit log records matching query expression

            :rtype: AuditLogPaginator
        """
        logging.info(f'function parameters - dataset_id: %s, expression: %s, limit: %s, offset: %s' % (dataset_id, expression, limit, offset))
        with kdp_api.ApiClient(config) as api_client:
            api_instance = workspaces_api.WorkspacesApi(api_client)

            query = LuceneQueryRequest(
              datasetId=dataset_id,
              expression=expression,
              limit=limit,
              offset=offset
            )

            return api_instance.post_audit_log_query(lucene_query_request=query)

