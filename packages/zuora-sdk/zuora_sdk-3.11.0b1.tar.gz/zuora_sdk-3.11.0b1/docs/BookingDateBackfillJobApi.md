# zuora_sdk.BookingDateBackfillJobApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**g_et_booking_date_backfill_job_by_id**](BookingDateBackfillJobApi.md#g_et_booking_date_backfill_job_by_id) | **GET** /v1/uno/data-backfill/bookingdate/jobs/{jobId} | Find BookingDate Backfill job by ID
[**g_et_list_booking_date_backfill_jobs**](BookingDateBackfillJobApi.md#g_et_list_booking_date_backfill_jobs) | **GET** /v1/uno/data-backfill/bookingdate/jobs | Query all Booking Date Backfill Jobs
[**p_ost_create_booking_date_backfill_job**](BookingDateBackfillJobApi.md#p_ost_create_booking_date_backfill_job) | **POST** /v1/uno/data-backfill/bookingdate/jobs | Create a new BookingDate Backfil job
[**p_ut_stop_booking_date_backfill_job_by_id**](BookingDateBackfillJobApi.md#p_ut_stop_booking_date_backfill_job_by_id) | **PUT** /v1/uno/data-backfill/bookingdate/jobs/{jobId} | Stop BookingDate Backfill job by ID


# **g_et_booking_date_backfill_job_by_id**
> GETBookingDateBackfillJobById200Response g_et_booking_date_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids)

Find BookingDate Backfill job by ID

Returns a single BookingDate Backfill job

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_booking_date_backfill_job_by_id200_response import GETBookingDateBackfillJobById200Response
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
    api_instance = zuora_sdk.BookingDateBackfillJobApi(api_client)
    job_id = 'job_id_example' # str | ID of job to return
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Find BookingDate Backfill job by ID
        api_response = api_instance.g_et_booking_date_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids)
        print("The response of BookingDateBackfillJobApi->g_et_booking_date_backfill_job_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BookingDateBackfillJobApi->g_et_booking_date_backfill_job_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**| ID of job to return | 
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**GETBookingDateBackfillJobById200Response**](GETBookingDateBackfillJobById200Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Response of BookingDate Backfill job by ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **g_et_list_booking_date_backfill_jobs**
> GETListBookingDateBackfillJobs200Response g_et_list_booking_date_backfill_jobs()

Query all Booking Date Backfill Jobs

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.get_list_booking_date_backfill_jobs200_response import GETListBookingDateBackfillJobs200Response
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
    api_instance = zuora_sdk.BookingDateBackfillJobApi(api_client)

    try:
        # Query all Booking Date Backfill Jobs
        api_response = api_instance.g_et_list_booking_date_backfill_jobs()
        print("The response of BookingDateBackfillJobApi->g_et_list_booking_date_backfill_jobs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BookingDateBackfillJobApi->g_et_list_booking_date_backfill_jobs: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**GETListBookingDateBackfillJobs200Response**](GETListBookingDateBackfillJobs200Response.md)

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

# **p_ost_create_booking_date_backfill_job**
> POSTCreateBookingDateBackfillJob200Response p_ost_create_booking_date_backfill_job()

Create a new BookingDate Backfil job

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.post_create_booking_date_backfill_job200_response import POSTCreateBookingDateBackfillJob200Response
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
    api_instance = zuora_sdk.BookingDateBackfillJobApi(api_client)

    try:
        # Create a new BookingDate Backfil job
        api_response = api_instance.p_ost_create_booking_date_backfill_job()
        print("The response of BookingDateBackfillJobApi->p_ost_create_booking_date_backfill_job:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BookingDateBackfillJobApi->p_ost_create_booking_date_backfill_job: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**POSTCreateBookingDateBackfillJob200Response**](POSTCreateBookingDateBackfillJob200Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | create booking job successfully |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **p_ut_stop_booking_date_backfill_job_by_id**
> CommonResponse p_ut_stop_booking_date_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids, put_stop_booking_date_backfill_job_by_id_request=put_stop_booking_date_backfill_job_by_id_request)

Stop BookingDate Backfill job by ID

Stop a single BookingDate Backfill job

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
    api_instance = zuora_sdk.BookingDateBackfillJobApi(api_client)
    job_id = 'job_id_example' # str | ID of job to stop
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    put_stop_booking_date_backfill_job_by_id_request = {"status":"Stopping"} # PUTStopBookingDateBackfillJobByIdRequest |  (optional)

    try:
        # Stop BookingDate Backfill job by ID
        api_response = api_instance.p_ut_stop_booking_date_backfill_job_by_id(job_id, zuora_org_ids=zuora_org_ids, put_stop_booking_date_backfill_job_by_id_request=put_stop_booking_date_backfill_job_by_id_request)
        print("The response of BookingDateBackfillJobApi->p_ut_stop_booking_date_backfill_job_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BookingDateBackfillJobApi->p_ut_stop_booking_date_backfill_job_by_id: %s\n" % e)
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
**200** | Response of Stopping BookingDate Backfill job by ID |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

