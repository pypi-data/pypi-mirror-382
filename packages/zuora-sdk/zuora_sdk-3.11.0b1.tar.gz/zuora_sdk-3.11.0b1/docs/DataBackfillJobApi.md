# zuora_sdk.DataBackfillJobApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**g_et_data_backfill_job_by_id**](DataBackfillJobApi.md#g_et_data_backfill_job_by_id) | **GET** /v1/uno/data-backfill/jobs/{jobId} | Find Data Backfill job by ID
[**g_et_data_backfill_template**](DataBackfillJobApi.md#g_et_data_backfill_template) | **GET** /v1/uno/data-backfill/jobs/{type}/template | Download a Data Backfill template file
[**g_et_list_data_backfill_jobs**](DataBackfillJobApi.md#g_et_list_data_backfill_jobs) | **GET** /v1/uno/date-backfill/listjobs | Query all data backfill jobs
[**p_ost_create_data_backfill_job**](DataBackfillJobApi.md#p_ost_create_data_backfill_job) | **POST** /v1/uno/data-backfill/jobs | Create a new Data Backfil job
[**p_ut_stop_data_backfill_job_by_id**](DataBackfillJobApi.md#p_ut_stop_data_backfill_job_by_id) | **PUT** /v1/uno/data-backfill/jobs/{jobId} | Stop Data Backfill job by ID


# **g_et_data_backfill_job_by_id**
> GETDataBackfillJobById200Response g_et_data_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids)

Find Data Backfill job by ID

Returns a single Data Backfill job

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_data_backfill_job_by_id200_response import GETDataBackfillJobById200Response
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
    api_instance = zuora_sdk.DataBackfillJobApi(api_client)
    job_id = 'job_id_example' # str | ID of job to return
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Find Data Backfill job by ID
        api_response = api_instance.g_et_data_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids)
        print("The response of DataBackfillJobApi->g_et_data_backfill_job_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataBackfillJobApi->g_et_data_backfill_job_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| ID of job to return | 
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**GETDataBackfillJobById200Response**](GETDataBackfillJobById200Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of Data Backfill job by ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **g_et_data_backfill_template**
> str g_et_data_backfill_template(type, zuora_org_ids=zuora_org_ids)

Download a Data Backfill template file

Download a Data Backfill template file by type

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.job_type import JobType
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
    api_instance = zuora_sdk.DataBackfillJobApi(api_client)
    type = zuora_sdk.JobType() # JobType | Type values of Data Backfill job
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Download a Data Backfill template file
        api_response = api_instance.g_et_data_backfill_template(type, zuora_org_ids=zuora_org_ids)
        print("The response of DataBackfillJobApi->g_et_data_backfill_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataBackfillJobApi->g_et_data_backfill_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | [**JobType**](.md)| Type values of Data Backfill job | 
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

**str**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/csv

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  * Content-Disposition - indicating it should be downloaded, prefilled with the value of the filename parameters if present <br>  * Zuora-Request-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **g_et_list_data_backfill_jobs**
> GETListDataBackfillJobs200Response g_et_list_data_backfill_jobs()

Query all data backfill jobs

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_list_data_backfill_jobs200_response import GETListDataBackfillJobs200Response
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
    api_instance = zuora_sdk.DataBackfillJobApi(api_client)

    try:
        # Query all data backfill jobs
        api_response = api_instance.g_et_list_data_backfill_jobs()
        print("The response of DataBackfillJobApi->g_et_list_data_backfill_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataBackfillJobApi->g_et_list_data_backfill_jobs: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GETListDataBackfillJobs200Response**](GETListDataBackfillJobs200Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | successful operation |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **p_ost_create_data_backfill_job**
> POSTCreateDataBackfillJob200Response p_ost_create_data_backfill_job(type, file, checksum=checksum)

Create a new Data Backfil job

A Data Backfill type and file are required

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.job import Job
from zuora_sdk.models.post_create_data_backfill_job200_response import POSTCreateDataBackfillJob200Response
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
    api_instance = zuora_sdk.DataBackfillJobApi(api_client)
    type = zuora_sdk.Job() # Job | 
    file = None # bytearray | File containing data about the data you want to backfill.  The file must be a `.csv` file or a zipped `.csv` file. The maximum file size is 4 MB. The data in the file must be formatted according to the Data Backfill type you want to perform.
    checksum = 'checksum_example' # str | An MD5 checksum that is used to validate the integrity of the uploaded file. (optional)

    try:
        # Create a new Data Backfil job
        api_response = api_instance.p_ost_create_data_backfill_job(type, file, checksum=checksum)
        print("The response of DataBackfillJobApi->p_ost_create_data_backfill_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataBackfillJobApi->p_ost_create_data_backfill_job: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | [**Job**](Job.md)|  | 
 **file** | **bytearray**| File containing data about the data you want to backfill.  The file must be a &#x60;.csv&#x60; file or a zipped &#x60;.csv&#x60; file. The maximum file size is 4 MB. The data in the file must be formatted according to the Data Backfill type you want to perform. | 
 **checksum** | **str**| An MD5 checksum that is used to validate the integrity of the uploaded file. | [optional] 

### Return type

[**POSTCreateDataBackfillJob200Response**](POSTCreateDataBackfillJob200Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | upload response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **p_ut_stop_data_backfill_job_by_id**
> CommonResponse p_ut_stop_data_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids, put_stop_booking_date_backfill_job_by_id_request=put_stop_booking_date_backfill_job_by_id_request)

Stop Data Backfill job by ID

Stop a single Data Backfill job

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.common_response import CommonResponse
from zuora_sdk.models.put_stop_booking_date_backfill_job_by_id_request import PUTStopBookingDateBackfillJobByIdRequest
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
    api_instance = zuora_sdk.DataBackfillJobApi(api_client)
    job_id = 'job_id_example' # str | ID of job to stop
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    put_stop_booking_date_backfill_job_by_id_request = {"status":"Stopping"} # PUTStopBookingDateBackfillJobByIdRequest |  (optional)

    try:
        # Stop Data Backfill job by ID
        api_response = api_instance.p_ut_stop_data_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids, put_stop_booking_date_backfill_job_by_id_request=put_stop_booking_date_backfill_job_by_id_request)
        print("The response of DataBackfillJobApi->p_ut_stop_data_backfill_job_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataBackfillJobApi->p_ut_stop_data_backfill_job_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| ID of job to stop | 
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **put_stop_booking_date_backfill_job_by_id_request** | [**PUTStopBookingDateBackfillJobByIdRequest**](PUTStopBookingDateBackfillJobByIdRequest.md)|  | [optional] 

### Return type

[**CommonResponse**](CommonResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of Stopping Data Backfill job by ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

