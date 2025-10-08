import kdp_api
from kdp_api.api.authenticate_api import AuthenticateApi
from kdp_api.api.authenticate_api import Authentication
from kdp_api.models.authentication_sso import AuthenticationSSO

from kdp_connector.configuration.keycloak_authentication import KeycloakAuthentication
from kdp_connector.configuration.proxy_authentication import ProxyAuthentication

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

class AuthenticationUtil(object):

    @staticmethod
    def create_authentication_token(config, email: str, password: str, workspace_id: str, strategy: str = 'local'):
        """This method will be used to create a KDP authentication token

            :param Configuration config: KDP configuration
            :param str email: User email address
            :param str password: User password
            :param str workspace_id: User workspace
            :param str strategy: Defaults to "local"

            :returns: Authentication token

            :rtype: AuthenticationDetails
        """

        with kdp_api.ApiClient(config) as api_client:
            api_instance = AuthenticateApi(api_client)

            authentication = Authentication(strategy=strategy, email=email, password=password, workspaceId=workspace_id)
            return api_instance.post_authentication(authentication=authentication)

    @staticmethod
    # only applicable if jwt is created for auth-proxy
    def create_proxy_authentication_token(config, first_name: str, workspace_id: str, strategy: str = 'proxy'):
        """This method will be used to create a KDP authentication token. Only request from auth-proxy with be accepted.

            :param str first_name: User's first name
            :param str workspace_id: User workspace
            :param str strategy: Defaults to "proxy"

            :returns: Authentication token

            :rtype: AuthenticationDetails
        """

        with kdp_api.ApiClient(config) as api_client:
            api_instance = AuthenticateApi(api_client)

            authentication = ProxyAuthentication(strategy=strategy, first_name=first_name, workspace_id=workspace_id)
            return api_instance.post_authentication(authentication=authentication)

    @staticmethod
    # only applicable if jwt is created for keycloak
    def get_koverse_token_from_keycloak_login(config, keycloak: KeycloakAuthentication, workspace_id: str):
      """This method will be used to create a KDP authentication token. Only request from auth-proxy with be accepted.

          :param object KeycloakConfiguration keycloak_config: Keycloak configuration
          :param str workspace_id: Koverse Workspace Id

          :returns: Koverse Authentication token

          :rtype: AuthenticationDetails
      """

      keycloak_token = keycloak.get_keycloak_token()
      with kdp_api.ApiClient(config) as api_client:
        api_instance = AuthenticateApi(api_client)
        authentication = AuthenticationSSO(strategy="keycloak", access_token=keycloak_token)

        return api_instance.post_authentication_sso(authentication_sso=authentication, workspace_id=workspace_id)




