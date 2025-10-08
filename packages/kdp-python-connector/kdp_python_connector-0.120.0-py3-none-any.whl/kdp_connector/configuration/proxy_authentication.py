from kdp_api.models.authentication import Authentication

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

"""
This class extends Authentication and override the strategy validation to allow
authentication request coming from auth-proxy service.
"""
class ProxyAuthentication(Authentication):

    def __init__(self, first_name: str, workspace_id: str, strategy: str, *args, **kwargs):
        super().__init__(email="", password="", firstName=first_name, workspaceId=workspace_id, strategy=strategy)
