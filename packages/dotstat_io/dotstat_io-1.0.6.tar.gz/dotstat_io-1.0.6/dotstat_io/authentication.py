import requests
import os
import msal
import requests_kerberos
import json
import time

from abc import ABC
from enum import IntEnum
from datetime import datetime

# 
class AuthenticationMode(IntEnum):
    INTERACTIVE = 1
    NONINTERACTIVE_WITH_SECRET = 2
    NONINTERACTIVE_WITH_ADFS = 3

# super class to manage authentication
class Authentication(ABC):

    # protected variables
    _access_token = None
    _refresh_token = None
    _creation_time = None
    _expiration_time = None

    # public variables
    init_status = None

    # Initialise authentication
    def __init__(
        self,
	    client_id: str,
        mode: AuthenticationMode,
        client_secret: str = None,
	    scopes: list[str] = [],
	    token_url: str = None,
        sdmx_resource_id: str = None,
        authority_url: str = None,
        redirect_port: int = 3000,
	    user: str = None,
        password: str = None,
        proxy: str = None
    ):
        self._client_id = client_id
        self._mode = mode
        self._client_secret = client_secret
        self._scopes = scopes     
        self._token_url = token_url
        self._sdmx_resource_id = sdmx_resource_id
        self._authority_url = authority_url
        self._redirect_port = redirect_port
        self._user = user
        self._password = password

        if proxy:
            self._proxies = {
                "http": proxy,
                "https": proxy
            }
        else:
            self._proxies = None

        #
        self._initialize_token()

    # 
    def __enter__(self):
        return self

    # 
    def __exit__(self, exc_type, exc_value, traceback):
        self._access_token = None
        self._refresh_token = None
        self._creation_time = None
        self._expiration_time = None
        self.init_status = None

    # 
    def _initialize_token(self):
        pass

    # 
    def get_token(self):
        if (self._access_token is None) \
               or (datetime.fromtimestamp(self._expiration_time) is not None \
                   and datetime.now() >= datetime.fromtimestamp(self._expiration_time)):
            self._initialize_token()

        return self._access_token


# sub class to manage ADFS authentication using OIDC flows
class AdfsAuthentication(Authentication):
    # private constants
    __ERROR_OCCURRED = "An error occurred: "
    __SUCCESSFUL_AUTHENTICATION = "Successful authentication"

    # 
    def _initialize_token(self):
        self._access_token = None
        self._refresh_token = None
        self._creation_time = None
        self._expiration_time = None
        self.init_status = None
        match self._mode:
            case AuthenticationMode.INTERACTIVE:
                self._app = msal.PublicClientApplication(
                    self._client_id, authority=self._authority_url)
                self.__acquire_token_interactive()
            case AuthenticationMode.NONINTERACTIVE_WITH_SECRET:
                self._app = msal.ConfidentialClientApplication(
                    self._client_id, authority=self._authority_url, client_credential=self._client_secret)
                self.__acquire_token_noninteractive_with_secret()
            case AuthenticationMode.NONINTERACTIVE_WITH_ADFS:
                self.__acquire_token_noninteractive_with_adfs()

    #           
    @classmethod
    def interactive(
        cls, 
        client_id: str, 
        sdmx_resource_id: str, 
        scopes: list[str], 
        authority_url: str, 
        redirect_port: int = 3000,
        mode: AuthenticationMode = AuthenticationMode.INTERACTIVE
    ):
        return cls(
            client_id=client_id, 
            sdmx_resource_id=sdmx_resource_id, 
            scopes=scopes, 
            authority_url=authority_url,
            redirect_port=redirect_port,
            mode=mode
        )

    #
    @classmethod
    def noninteractive_with_secret(
        cls, 
        client_id: str, 
        sdmx_resource_id: str,
        scopes: list[str],
        authority_url: str,
        client_secret: str,
        mode: AuthenticationMode = AuthenticationMode.NONINTERACTIVE_WITH_SECRET
    ):
        return cls(
            client_id=client_id,
            sdmx_resource_id=sdmx_resource_id,
            scopes=scopes,
            authority_url=authority_url,   
            client_secret=client_secret,  
            mode=mode
            )

    #
    @classmethod
    def noninteractive_with_adfs(
        cls, 
        client_id: str, 
        sdmx_resource_id: str,
        token_url: str,
        mode: AuthenticationMode = AuthenticationMode.NONINTERACTIVE_WITH_ADFS
    ):
        return cls(
            client_id=client_id, 
            sdmx_resource_id=sdmx_resource_id,
            token_url=token_url,
            mode=mode)

    # Authentication interactively - aka Authorization Code flow
    def __acquire_token_interactive(self):
        try:
            # We now check the cache to see
            # whether we already have some accounts that the end user already used to sign in before.
            accounts = self._app.get_accounts()
            if accounts:
                account = accounts[0]
            else:
                account = None

            # Firstly, looks up a access_token from cache, or using a refresh token
            response_silent = self._app.acquire_token_silent(
                self._scopes, account=account)
            if not response_silent:
                # Prompt the user to sign in interactively
                response_interactive = self._app.acquire_token_interactive(
                    scopes=self._scopes, port=self._redirect_port)
                if "access_token" in response_interactive:
                    self._access_token = response_interactive.get("access_token")
                    self._refresh_token = response_interactive.get("refresh_token")
                    self._creation_time = time.time()
                    self._expiration_time = time.time() + int(response_interactive.get("expires_in")) -  60 # one minute margin
                    self.init_status = self.__SUCCESSFUL_AUTHENTICATION
                else:
                    self.init_status = f'{self.__ERROR_OCCURRED}{response_interactive.get("error")} Error description: {response_interactive.get("error_description")}'
            else:
                if "access_token" in response_silent:
                    self._access_token = response_silent.get("access_token")
                    self._refresh_token = response_silent.get("refresh_token")
                    self._creation_time = time.time()
                    self._expiration_time = time.time() + int(response_silent.get("expires_in")) -  60 # one minute margin
                    self.init_status = self.__SUCCESSFUL_AUTHENTICATION
                else:
                    self.init_status = f'{self.__ERROR_OCCURRED}{response_silent.get("error")} Error description: {response_silent.get("error_description")}'
        except Exception as err:
            self.init_status = f'{self.__ERROR_OCCURRED}{err}\n'

    # Authentication non-interactively using any account - aka Client Credentials flow
    def __acquire_token_noninteractive_with_secret(self):
        try:
            response = self._app.acquire_token_for_client(scopes=self._scopes)
            if "access_token" in response:
                self._access_token = response.get("access_token")
                self._creation_time = time.time()
                self._expiration_time = time.time() + int(response.get("expires_in")) -  60 # one minute margin
                self.init_status = self.__SUCCESSFUL_AUTHENTICATION
            else:
                self.init_status = f'{self.__ERROR_OCCURRED}{response.get("error")} Error description: {response.get("error_description")}'

        except Exception as err:
            self.init_status = f'{self.__ERROR_OCCURRED}{err}\n'

    # Authentication non-interactively using service account - aka Windows Client Authentication
    def __acquire_token_noninteractive_with_adfs(self):
        try:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                'client_id': self._client_id,
                'use_windows_client_authentication': 'true',
                'grant_type': 'client_credentials',
                'scope': 'openid',
                'resource': self._sdmx_resource_id
            }

            kerberos_auth = requests_kerberos.HTTPKerberosAuth(
                mutual_authentication=requests_kerberos.OPTIONAL, force_preemptive=True)
            response = requests.post(url=self._token_url, data=payload, auth=kerberos_auth)

            # If the response object cannot be converted to json, return an error
            results_json = None
            try:
                results_json = json.loads(response.text)
                if response.status_code == 200:
                    self._access_token = results_json['access_token']
                    self._creation_time = time.time()
                    self._expiration_time = time.time() + int(results_json['expires_in']) -  60 # one minute margin
                    self.init_status = self.__SUCCESSFUL_AUTHENTICATION
                else:
                    message = f'{self.__ERROR_OCCURRED} Error code: {response.status_code}'
                    if len(str(response.reason)) > 0:
                        message += os.linesep + 'Reason: ' + str(response.reason) + os.linesep
                    if len(response.text) > 0:
                        message += f'{self.__ERROR_OCCURRED}{results_json.get("error")} Error description: {results_json.get("error_description")}\n'
                        
                    self.init_status = message
            except ValueError as err:
               self.init_status = self.__ERROR_OCCURRED + os.linesep
               if len(str(response.status_code)) > 0:
                  self.init_status += 'Error code: ' + str(response.status_code) + os.linesep
               if len(str(response.reason)) > 0:
                  self.init_status += 'Reason: ' + str(response.reason) + os.linesep
               if len(response.text) > 0:
                  self.init_status += str(response.text)
               else:
                  self.init_status += str(err)
        except Exception as err:
            self.init_status = f'{self.__ERROR_OCCURRED} {err}\n'


# sub class to manage Keycloak authentication
class KeycloakAuthentication(Authentication):
    # private constants
    __ERROR_OCCURRED = "An error occurred: "
    __SUCCESSFUL_AUTHENTICATION = "Successful authentication"
 
    #
    def _initialize_token(self):
        self._access_token = None
        self._refresh_token = None
        self._creation_time = None
        self._expiration_time = None
        self.init_status = None
        match self._mode:
            case AuthenticationMode.NONINTERACTIVE_WITH_SECRET:
                self.__acquire_token_noninteractive_with_secret()

    #
    @classmethod
    def noninteractive_with_secret(
        cls, 
        token_url: str,
        user: str,
        password: str,
        client_id: str = "app",
        client_secret: str = "",
        proxy: str | None = None,
        scopes: list[str] = [],
        mode: AuthenticationMode = AuthenticationMode.NONINTERACTIVE_WITH_SECRET
    ):
        return cls(           
            token_url=token_url,
            user=user,
            password=password,
            client_id=client_id,   
            client_secret=client_secret,
            scopes=scopes,
            proxy=proxy,  
            mode=mode
            )

    # Authentication non-interactively using any account - aka Client Credentials flow
    def __acquire_token_noninteractive_with_secret(self):
        try:
            payload = {
            'grant_type': 'password',
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'username': self._user,
            'password': self._password
            }

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(self._token_url, proxies=self._proxies, headers=headers, data=payload)
            if response.status_code not in {200, 201}:
                self.init_status = f'{self.__ERROR_OCCURRED}{response}'
            else:
                # If the response object cannot be converted to json, return an error
                results_json = None
                try:
                    results_json = json.loads(response.text)
                    self._access_token = results_json['access_token']
                    self._refresh_token = results_json['refresh_token']
                    self._creation_time = time.time()
                    self._expiration_time = time.time() + int(results_json['expires_in']) -  60 # one minute margin
                    self.init_status = self.__SUCCESSFUL_AUTHENTICATION
                except ValueError as err:
                  self.init_status = self.__ERROR_OCCURRED + os.linesep
                  if len(str(response.status_code)) > 0:
                     self.init_status += 'Error code: ' + str(response.status_code) + os.linesep
                  if len(str(response.reason)) > 0:
                     self.init_status += 'Reason: ' + str(response.reason) + os.linesep
                  if len(response.text) > 0:
                     self.init_status += str(response.text)
                  else:
                     self.init_status += str(err)
        except Exception as err:
            self.init_status = f'{self.__ERROR_OCCURRED}{err}\n'
