# zuora_sdk.RevenueIntegrationApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**describe_view_columns**](RevenueIntegrationApi.md#describe_view_columns) | **GET** /integration/v2/biviews/{view_name}/describe-columns | 
[**download_report**](RevenueIntegrationApi.md#download_report) | **GET** /integration/v1/reports/download/{filename} | 
[**generate_jwt_token**](RevenueIntegrationApi.md#generate_jwt_token) | **POST** /integration/v1/authenticate | 
[**get_bi_view_count**](RevenueIntegrationApi.md#get_bi_view_count) | **GET** /integration/v2/biviews/count/{view_name} | 
[**get_bi_view_status**](RevenueIntegrationApi.md#get_bi_view_status) | **GET** /integration/v2/biviews-status | 
[**get_bi_view_task_details**](RevenueIntegrationApi.md#get_bi_view_task_details) | **GET** /integration/v2/biviews-status/{task_id} | 
[**get_bi_views**](RevenueIntegrationApi.md#get_bi_views) | **GET** /integration/v1/biviews/{view_name} | 
[**get_bi_views_v2**](RevenueIntegrationApi.md#get_bi_views_v2) | **GET** /integration/v2/biviews/{view_name} | 
[**get_csv_upload_status**](RevenueIntegrationApi.md#get_csv_upload_status) | **GET** /integration/v1/csv/upload/status | 
[**get_file_upload_status_by_request_id**](RevenueIntegrationApi.md#get_file_upload_status_by_request_id) | **GET** /integration/v1/fileupload/status/{file_request_id} | 
[**get_reports_by_id**](RevenueIntegrationApi.md#get_reports_by_id) | **GET** /integration/v1/reports/{report_id} | 
[**get_stage_error**](RevenueIntegrationApi.md#get_stage_error) | **GET** /integration/v1/stage/error/{errortype} | 
[**integration_v2_reports_signedurl_report_id_get**](RevenueIntegrationApi.md#integration_v2_reports_signedurl_report_id_get) | **GET** /integration/v2/reports/signedurl/{report_id} | 
[**list_reports**](RevenueIntegrationApi.md#list_reports) | **GET** /integration/v1/reports/list | 
[**select_bi_view**](RevenueIntegrationApi.md#select_bi_view) | **POST** /integration/v1/biviews/{view_name} | 
[**upload_csv**](RevenueIntegrationApi.md#upload_csv) | **POST** /integration/v1/csv/upload | 
[**upload_file**](RevenueIntegrationApi.md#upload_file) | **POST** /integration/v1/upload/file | 
[**upload_mapping**](RevenueIntegrationApi.md#upload_mapping) | **POST** /integration/v1/upload/mapping | 


# **describe_view_columns**
> List[Bi3ViewsColumnsDescriptionResponse] describe_view_columns(view_name, token)



Use this API to get the table description for views.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi3_views_columns_description_response import Bi3ViewsColumnsDescriptionResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    view_name = 'view_name_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 

    try:
        api_response = api_instance.describe_view_columns(view_name, token)
        print("The response of RevenueIntegrationApi->describe_view_columns:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->describe_view_columns: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view_name** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**List[Bi3ViewsColumnsDescriptionResponse]**](Bi3ViewsColumnsDescriptionResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Table attributes retrieved successfully. |  -  |
**204** | No Content - No data found for the view. |  -  |
**400** | Invalid user or template name. |  -  |
**500** | Server error - Unable to process the request. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_report**
> download_report(token, filename)



Use this API to Download Reports from RevPro

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    filename = 'filename_example' # str | download report name

    try:
        api_instance.download_report(token, filename)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->download_report: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **filename** | **str**| download report name | 

### Return type

void (empty response body)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Operation is successful. Report is downloaded. |  -  |
**204** | The specified file does not exist in Zuora Revenue. |  -  |
**400** | Returns if File name doesn&#39;t exist in path |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **generate_jwt_token**
> AuthenticationSuccessResponse generate_jwt_token(role, clientname, authorization)



Use this API to Authenticate and get JWToken to push and pull data from your RevPro instance

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.authentication_success_response import AuthenticationSuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    role = 'API Role' # str |  (default to 'API Role')
    clientname = 'Default' # str |  (default to 'Default')
    authorization = 'Basic c3lzYWRtaW46UmV2cHJvJTEyMw==' # str | 

    try:
        api_response = api_instance.generate_jwt_token(role, clientname, authorization)
        print("The response of RevenueIntegrationApi->generate_jwt_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->generate_jwt_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role** | **str**|  | [default to &#39;API Role&#39;]
 **clientname** | **str**|  | [default to &#39;Default&#39;]
 **authorization** | **str**|  | 

### Return type

[**AuthenticationSuccessResponse**](AuthenticationSuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Token Generated |  -  |
**400** | Invalid Revpro Client name |  -  |
**401** | Invalid User Name or Password |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bi_view_count**
> Bi3ViewsCountSuccessResponse get_bi_view_count(view_name, token, from_date=from_date, to_date=to_date, pagenum=pagenum)



Use this API to get the record count for BI Views based on the template name.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi3_views_count_success_response import Bi3ViewsCountSuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    view_name = 'view_name_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 
    from_date = '2013-10-20' # date |  (optional)
    to_date = '2013-10-20' # date |  (optional)
    pagenum = 56 # int |  (optional)

    try:
        api_response = api_instance.get_bi_view_count(view_name, token, from_date=from_date, to_date=to_date, pagenum=pagenum)
        print("The response of RevenueIntegrationApi->get_bi_view_count:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_bi_view_count: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view_name** | **str**|  | 
 **token** | **str**|  | 
 **from_date** | **date**|  | [optional] 
 **to_date** | **date**|  | [optional] 
 **pagenum** | **int**|  | [optional] 

### Return type

[**Bi3ViewsCountSuccessResponse**](Bi3ViewsCountSuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Record Count Retrieved Successfully |  -  |
**400** | Invalid input or missing query parameters |  -  |
**500** | Server Error - Unable to process the request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bi_view_status**
> List[GetBIViewStatus200ResponseInner] get_bi_view_status(token)



Get details for the active running task.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_bi_view_status200_response_inner import GetBIViewStatus200ResponseInner
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 

    try:
        api_response = api_instance.get_bi_view_status(token)
        print("The response of RevenueIntegrationApi->get_bi_view_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_bi_view_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**|  | 

### Return type

[**List[GetBIViewStatus200ResponseInner]**](GetBIViewStatus200ResponseInner.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully retrieved BI View status. |  -  |
**204** | No Content - No active tasks found. |  -  |
**400** | Invalid user id or other parameters. |  -  |
**500** | Server error - Unable to process the request. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bi_view_task_details**
> Bi3ViewsTaskStatusResponse get_bi_view_task_details(task_id, token)



Get details for the active running task by task ID.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi3_views_task_status_response import Bi3ViewsTaskStatusResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    task_id = 'task_id_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 

    try:
        api_response = api_instance.get_bi_view_task_details(task_id, token)
        print("The response of RevenueIntegrationApi->get_bi_view_task_details:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_bi_view_task_details: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_id** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**Bi3ViewsTaskStatusResponse**](Bi3ViewsTaskStatusResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully retrieved task details. |  -  |
**204** | No Content - Task not found or no details available. |  -  |
**400** | Invalid user id or other parameters. |  -  |
**500** | Server error - Unable to process the request. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bi_views**
> BiViews1SuccessResponse get_bi_views(view_name, token)



Use this API to get BI Views based on template name.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi_views1_success_response import BiViews1SuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    view_name = 'view_name_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 

    try:
        api_response = api_instance.get_bi_views(view_name, token)
        print("The response of RevenueIntegrationApi->get_bi_views:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_bi_views: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view_name** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**BiViews1SuccessResponse**](BiViews1SuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | BI Views Retrieved Successfully |  -  |
**400** | Invalid User ID or Template Name |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bi_views_v2**
> Bi3ViewsV2SuccessResponse get_bi_views_v2(view_name, token, from_date=from_date, to_date=to_date, pagenum=pagenum)



Use this API to get BI Views based on view name.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi3_views_v2_success_response import Bi3ViewsV2SuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    view_name = 'view_name_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 
    from_date = '2013-10-20' # date |  (optional)
    to_date = '2013-10-20' # date |  (optional)
    pagenum = 56 # int |  (optional)

    try:
        api_response = api_instance.get_bi_views_v2(view_name, token, from_date=from_date, to_date=to_date, pagenum=pagenum)
        print("The response of RevenueIntegrationApi->get_bi_views_v2:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_bi_views_v2: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view_name** | **str**|  | 
 **token** | **str**|  | 
 **from_date** | **date**|  | [optional] 
 **to_date** | **date**|  | [optional] 
 **pagenum** | **int**|  | [optional] 

### Return type

[**Bi3ViewsV2SuccessResponse**](Bi3ViewsV2SuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | BI Views Retrieved Successfully |  -  |
**204** | No Data Available |  -  |
**400** | Query parameter missing or invalid input |  -  |
**404** | No data found or page does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_csv_upload_status**
> UploadCsvStatusResponse get_csv_upload_status(id, token)



Use this API to get the csv upload status

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.upload_csv_status_response import UploadCsvStatusResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    id = 'id_example' # str | File id for which status to be fetched
    token = 'token_example' # str | Authorization token issued by the authentication API

    try:
        api_response = api_instance.get_csv_upload_status(id, token)
        print("The response of RevenueIntegrationApi->get_csv_upload_status:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_csv_upload_status: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| File id for which status to be fetched | 
 **token** | **str**| Authorization token issued by the authentication API | 

### Return type

[**UploadCsvStatusResponse**](UploadCsvStatusResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The status information is returned for the requested upload. |  -  |
**204** | No Data Found for the Csv |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_upload_status_by_request_id**
> UploadFileStatusResponse get_file_upload_status_by_request_id(token, file_request_id)



Use this API to get file upload status from RevPro

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.upload_file_status_response import UploadFileStatusResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    file_request_id = 56 # int | File Request id

    try:
        api_response = api_instance.get_file_upload_status_by_request_id(token, file_request_id)
        print("The response of RevenueIntegrationApi->get_file_upload_status_by_request_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_file_upload_status_by_request_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **file_request_id** | **int**| File Request id | 

### Return type

[**UploadFileStatusResponse**](UploadFileStatusResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The status information is returned for the requested file upload. |  -  |
**204** | The status information cannot be retrieved for the specified request ID. |  -  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_reports_by_id**
> ReportListResponse get_reports_by_id(report_id, token, createddate)



Use this API to Fetch List of Reports available for provided date

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.report_list_response import ReportListResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    report_id = 'report_id_example' # str | Report Submission Id in Zuora Revenue
    token = 'token_example' # str | Authorization token issued by the authentication API
    createddate = '2013-10-20' # date | date when report was created

    try:
        api_response = api_instance.get_reports_by_id(report_id, token, createddate)
        print("The response of RevenueIntegrationApi->get_reports_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_reports_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **report_id** | **str**| Report Submission Id in Zuora Revenue | 
 **token** | **str**| Authorization token issued by the authentication API | 
 **createddate** | **date**| date when report was created | 

### Return type

[**ReportListResponse**](ReportListResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns when reports are available for the provided date |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stage_error**
> StageErrorResponse get_stage_error(token, errortype)



Use this API to get the staging error data for transaction or event type

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.stage_error_response import StageErrorResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    errortype = 'event/transaction' # str | error type (default to 'event/transaction')

    try:
        api_response = api_instance.get_stage_error(token, errortype)
        print("The response of RevenueIntegrationApi->get_stage_error:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->get_stage_error: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **errortype** | **str**| error type | [default to &#39;event/transaction&#39;]

### Return type

[**StageErrorResponse**](StageErrorResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Stage error response |  -  |
**204** | No record is found for the error type specified in the path parameter. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **integration_v2_reports_signedurl_report_id_get**
> SignedUrlSuccessResponse integration_v2_reports_signedurl_report_id_get(token, report_id)



Generates a signed URL from Zuora Revenue to download the report with the specified report ID. The returned URL will be valid for 30 minutes.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.signed_url_success_response import SignedUrlSuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    report_id = 'report_id_example' # str | Report Submission Id in Zuora Revenue

    try:
        api_response = api_instance.integration_v2_reports_signedurl_report_id_get(token, report_id)
        print("The response of RevenueIntegrationApi->integration_v2_reports_signedurl_report_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->integration_v2_reports_signedurl_report_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **report_id** | **str**| Report Submission Id in Zuora Revenue | 

### Return type

[**SignedUrlSuccessResponse**](SignedUrlSuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Signed Url Response |  -  |
**400** | The report ID is invalid. |  -  |
**404** | The specified report ID is not found. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_reports**
> ReportListResponse list_reports(token, createddate)



Use this API to Fetch List of Reports available for provided date

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.report_list_response import ReportListResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    createddate = '2013-10-20' # date | date when report was created

    try:
        api_response = api_instance.list_reports(token, createddate)
        print("The response of RevenueIntegrationApi->list_reports:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->list_reports: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **createddate** | **date**| date when report was created | 

### Return type

[**ReportListResponse**](ReportListResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns when reports are available for the provided date |  -  |
**400** | Returns if date format is wrong |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **select_bi_view**
> BiViews1SelectSuccessResponse select_bi_view(view_name, token)



Use this API to select specific BI View data.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.bi_views1_select_success_response import BiViews1SelectSuccessResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    view_name = 'view_name_example' # str | 
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' # str | 

    try:
        api_response = api_instance.select_bi_view(view_name, token)
        print("The response of RevenueIntegrationApi->select_bi_view:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->select_bi_view: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **view_name** | **str**|  | 
 **token** | **str**|  | 

### Return type

[**BiViews1SelectSuccessResponse**](BiViews1SelectSuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Selected BI View Data Retrieved Successfully |  -  |
**400** | Invalid User ID or Template Name |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_csv**
> UploadCsvResponse upload_csv(token, templatename, filename, body)



Use this API to upload the Transaction/Events/Bundle config data in csv format into RevPro

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.upload_csv_response import UploadCsvResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    templatename = 'templatename_example' # str | File Template name
    filename = 'filename_example' # str | File name
    body = 'body_example' # str | Raw CSV data to be uploaded

    try:
        api_response = api_instance.upload_csv(token, templatename, filename, body)
        print("The response of RevenueIntegrationApi->upload_csv:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->upload_csv: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **templatename** | **str**| File Template name | 
 **filename** | **str**| File name | 
 **body** | **str**| Raw CSV data to be uploaded | 

### Return type

[**UploadCsvResponse**](UploadCsvResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: text/plain
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Data is uploaded to the staging tables in Zuora Revenue. |  -  |
**400** | Error occurs when data is being uploaded to Zuora Revenue staging tables. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_file**
> UploadRevenueFileResponse upload_file(token, templatename, var_async=var_async, file=file)



Use this API to Upload csv files to RevPro

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.upload_revenue_file_response import UploadRevenueFileResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    templatename = 'templatename_example' # str | File template name
    var_async = 'var_async_example' # str | Set to true to perform the upload asynchronously. (optional)
    file = None # bytearray | The file to be uploaded. (optional)

    try:
        api_response = api_instance.upload_file(token, templatename, var_async=var_async, file=file)
        print("The response of RevenueIntegrationApi->upload_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->upload_file: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **templatename** | **str**| File template name | 
 **var_async** | **str**| Set to true to perform the upload asynchronously. | [optional] 
 **file** | **bytearray**| The file to be uploaded. | [optional] 

### Return type

[**UploadRevenueFileResponse**](UploadRevenueFileResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The file is uploaded to Zuora Revenue. |  -  |
**400** | Exception occurs. Please contact Zuora Revenue Support. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_mapping**
> MappingResponse upload_mapping(token, templatename)



Use this API to get Transaction/Events/Bundle upload mapping information from RevPro

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.mapping_response import MappingResponse
from zuora_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://rest.zuora.com
# See configuration.py for a list of all supported configuration parameters.
configuration = zuora_sdk.Configuration(
    host = "https://rest.zuora.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: bearerAuth
configuration = zuora_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with zuora_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = zuora_sdk.RevenueIntegrationApi(api_client)
    token = 'token_example' # str | Authorization token issued by the authentication API
    templatename = 'templatename_example' # str | Template name for mapping

    try:
        api_response = api_instance.upload_mapping(token, templatename)
        print("The response of RevenueIntegrationApi->upload_mapping:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RevenueIntegrationApi->upload_mapping: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token** | **str**| Authorization token issued by the authentication API | 
 **templatename** | **str**| Template name for mapping | 

### Return type

[**MappingResponse**](MappingResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Upload Mapping response |  -  |
**400** | Returns errors. Example - Exception during Upload Mapping error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

