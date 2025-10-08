import logging

import kdp_api
from kdp_api.api import workspaces_api
from kdp_api.configuration import Configuration
from kdp_api.models.audit_log_configuration import AuditLogConfiguration
from kdp_api.models.audit_log_configuration_paginator import AuditLogConfigurationPaginator

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

class AuditLogConfigsApi(object):
    def __init__(self, configuration: Configuration=None):
        self.configuration = configuration


    def get_audit_log_configs(self, config, keep_forever:bool = None, workspace_id:str = None,
        limit:int = 10, skip:int = 0, sort:object=None, filter:object=None) -> AuditLogConfigurationPaginator:
        """This method returns a AuditLogConfigurationPaginator object which contains list of AuditLogConfiguration objects.

            :param Configuration config: Connection configuration
            :param bool keep_forever: filter on keepForever flag.
            :param str workspace_id: filter on workspace ID.
            :param int limit: max number of results in the response.
            :param int skip: how many records to skip before returning first record.
            :returns: AuditLogConfigurationPaginator object

            :rtype: AuditLogConfigurationPaginator
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = workspaces_api.WorkspacesApi(api_client)

            logging.info(f'function parameters - keep_forever: %s, workspace_id: %s, limit: %s, skip: %s' % (keep_forever, workspace_id, limit, skip))

            if keep_forever is not None and workspace_id is not None:
                return api_instance.get_all_auditlog_configurations(
                    keep_forever=keep_forever,
                    workspace_id=workspace_id,
                    limit=limit,
                    skip=skip
                    )
            elif keep_forever is None and workspace_id is not None:
                return api_instance.get_all_auditlog_configurations(
                    workspace_id=workspace_id,
                    limit=limit,
                    skip=skip
                    )
            elif keep_forever is not None and workspace_id is None:
                return api_instance.get_all_auditlog_configurations(
                    keep_forever=keep_forever,
                    limit=limit,
                    skip=skip
                    )
            else:
                return api_instance.get_all_auditlog_configurations(
                    limit=limit,
                    skip=skip
                    )


    def patch_audit_log_configs(self, config, id:str, keep_forever:bool, age_in_days: int) -> AuditLogConfiguration:
        """This method updates AuditLogConfiguration object.

            :param Configuration config: Connection configuration
            :param str id: audit log config id
            :param bool keep_forever: keepForever flag.
            :param int age_in_days: number of days to keep the records if keep_forever flag is false.
            :returns: AuditLogConfiguration object after the update.

            :rtype: AuditLogConfiguration
        """
        logging.info(f'function parameters - id: %s, keep_forever: %s, age_in_days: %s' % (id, keep_forever, age_in_days))
        with kdp_api.ApiClient(config) as api_client:
            api_instance = workspaces_api.WorkspacesApi(api_client)
            audit_log_configuration: AuditLogConfiguration = AuditLogConfiguration(keep_forever=keep_forever, age_in_days=age_in_days)
            return api_instance.patch_auditlog_configuration(audit_log_configs_id=id, audit_log_configuration=audit_log_configuration)

