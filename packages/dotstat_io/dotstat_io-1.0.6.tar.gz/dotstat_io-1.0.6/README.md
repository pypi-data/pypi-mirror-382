### DotStat_IO package: 
A generic python package which could be integrated with other end-user applications and Gitlab runner to perform basic io with .Stat Suite. 
Its role is to mask the complexities of authentication to connect to .Stat Suite.
The user needs to provide a set of parameters and the package exposes a couple of methods which will download or upload data from/to .Stat Suite.

### This package contains three modules:
- ADFSAuthentication module
- KeycloakAuthentication module
- Client module

### In ADFSAuthentication module, four methods are available:
#### 1. To initialise the module for interactive use:
```python
from dotstat_io.authentication import AdfsAuthentication
interactive_obj = AdfsAuthentication.interactive(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        scopes=scopes,
        authority_url=authority_url,
        redirect_port=redirect_port)

```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `redirect_port:` The port of the address to return to upon receiving a response from the authority

#### 2. To initialise the module for non-interactive use using a secret: 
```python
from dotstat_io.authentication import AdfsAuthentication
noninteractive_with_secret_obj = AdfsAuthentication.noninteractive_with_secret(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        scopes=scopes,
        authority_url=authority_url,
        client_secret=client_secret)

```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite
* `scopes:` Scopes requested to access a protected API (a resource defined by sdmx_resource_id)
* `authority_url:` URL that identifies a token authority
* `client_secret:` The application secret that you created during app registration in ADFS

#### 3. To initialise the module for non-interactive use using windows client authentication:
```python
from dotstat_io.authentication import AdfsAuthentication
noninteractive_with_adfs_obj = AdfsAuthentication.noninteractive_with_adfs(
        client_id=client_id,
        sdmx_resource_id=sdmx_resource_id,
        token_url=token_url)

```
* `client_id:` The Application (client) ID that the ADFS assigned to your app
* `sdmx_resource_id:` The ID of the application to be accessed such as .Stat Suite
* `token_url:` URL of the authentication service

#### 4. To get a token after initialisation of "AdfsAuthentication" object as shown above: 
```python
access_token = [Authentication Object Name].get_token()
```

### In KeycloakAuthentication module, two methods are available:
#### 1. To initialise the module for Keycloak authentication:
```python
from dotstat_io.authentication import KeycloakAuthentication
noninteractive_with_keycloak_obj = KeycloakAuthentication.noninteractive_with_secret(
        user=user,
        password=password, 
        token_url=token_url, 
        proxy=proxy)

```
* `user:` User name for .Stat Suite authentication
* `password:` User name's password
* `token_url:` URL of the authentication service
* `proxy:` URL of the SSL certificates

#### 2. To get a token after initialisation of "KeycloakAuthentication" object as shown above: 
```python
access_token = [Authentication Object Name].get_token()
```

### In Client module, six methods are available:
#### 1. To initialise the module using an Authentication object type AdfsAuthentication or KeycloakAuthentication:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
```
* `Authentication_obj:` An initialized authentication object type AdfsAuthentication or KeycloakAuthentication

#### 2. To initialise the module using an access token:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_access_token(access_token)
```
* `access_token:` An access token to make requests on .Stat Suite services (nsiws) using the authorisation service and underlying permission rules

#### 3. To download a file from .Stat Suite:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
returned_result = client_obj.download_data_file(
        dotstat_url, content_format, Path(file_path))
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content
* `file_path:` The full path where the file will downloaded

#### 4. To download streamed content from .Stat Suite:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
returned_result = client_obj.download_data_stream(
        dotstat_url, content_format)
```
* `dotstat_url:` URL of data to be downloaded from .Stat Suite
* `content_format:` Format of the downloaded content

#### 5. To upload a data file to .Stat Suite:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
returned_result = client_obj.upload_data_file(
        transfer_url, Path(file_path), space, validationType, use_filepath, optimize)
```
* `transfer_url:` URL of the transfer service
* `file_path:` The full path of the SDMX-CSV file to be imported
* `space:` Data space where the file will be uploaded
* `validationType:` The type of validation to use during upload. Possible values: Basic Validation (0), Advanced Validation (1)
* `use_filepath:` Use a file path of a shared folder accessible by the .Stat Suite data upload engine (for unlimited file sizes)
* `optimize:` Controls whether optimization is applied after data changes

#### 6. To upload an Excel data file to .Stat Suite:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
returned_result = client_obj.upload_excel_data_file(
        transfer_url, Path(excelfile_path), Path(eddfile_path), space, validationType)
```
* `transfer_url:` URL of the transfer service
* `excelfile_path:` The full path of the Excel file containing the data/referential metadata values to be imported
* `eddfile_path:` The full path of the XML edd file containing the description of the Excel file to be imported
* `space:` Data space where the file will be uploaded
* `validationType:` The type of validation to use during upload. Possible values: Basic Validation (0), Advanced Validation (1)

#### 7. To upload a structure to .Stat Suite:
```python
from dotstat_io.client import Client
client_obj = Client.init_with_authentication_obj(Authentication_obj)
returned_result = client_obj.upload_structure(
        transfer_url, Path(file_path))
```
* `transfer_url:` URL of the transfer service
* `file_path:` The full path of the SDMX-ML file to be imported

### For more information about how to use this package, all test cases can be accessed from this [`link`](https://gitlab.algobank.oecd.org/SD_ENGINEERING/dotstat_io/dotstat_io-package/-/blob/main/tests/test_cases.py)
