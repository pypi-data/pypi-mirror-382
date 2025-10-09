# zuora_sdk.SettingsApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_list_all_settings**](SettingsApi.md#get_list_all_settings) | **GET** /settings/listing | List all settings
[**post_process_settings_batch_request**](SettingsApi.md#post_process_settings_batch_request) | **POST** /settings/batch-requests | Submit settings requests


# **get_list_all_settings**
> ListAllSettingsResponse get_list_all_settings(accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, accept=accept, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

List all settings

Get a list of all available settings in your tenant.   The response message is by default in JSON format. If you want to receive all the available settings in csv format, include `Accept` in the header parameters and set it to `application/csv`.              See a [200 response sample in JSON format](https://www.zuora.com/developer/settings-api/ListAllSettingsResponseSample.json) that lists all available settings.   See a [200 response sample in CSV format](https://www.zuora.com/developer/settings-api/ListAllSettingsResponseSample.csv) that lists all available settings.  You can find a specific operation of an available setting item in your tenant from the 200 response body of this call. See the following common use cases of Settings API for how to operate on a specifc setting item.   * Billing Rules:    * [Get a specific setting - Billing Rules](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/AA_Get_a_specific_setting_-_Billing_Rules)    * [Update a specific setting - Billing Rules](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/AB_Update_a_specific_setting_-_Billing_Rules)  * Age Buckets:    * [Get Age Buckets](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Get_Age_Buckets)    * [Update Age Buckets](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Update_Age_Buckets)  * Invoice Templates:    * [Get a specific Invoice Template](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Get_a_specific_Invoice_Template)    * [Get all Invoice Templates](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Get_all_Invoice_Templates)    * [Create a new Invoice Template](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Create_a_new_Invoice_Template)    * [Update a specific Invoice Template](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Update_a_specific_Invoice_Template)    * [Delete a specific Invoice Template](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Delete_a_specific_Invoice_Template)  * Communications Profiles:    * [Create a new Communication Profile](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Create_a_new_Communication_Profile)    * [Get a Communication Profile](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_a_Communication_Profile)    * [Get all Communication Profiles](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Get_all_Communication_Profiles)    * [Modify a Communication Profile](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Modify_a_Communication_Profile)  * Notification Definitions:    * [Get all notification definitions under a particular Communication Profile](https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_all_Notifications_under_a_particular_Communication_Profile)    * [Get a notification definition](https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_a_notification_definition)    * [Update a notification definition](https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Update_a_notification_definition)    * [Delete a notification definition](https://knowledgecenter.zuora.com/Zuora_Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Delete_a_notification_definition)  * Chart of Accounts:    * [Get Chart of Accounts](https://knowledgecenter.zuora.com/DC_Developers/BB_C_Settings_API/Settings_API_tutorials/Get_Chart_of_Accounts)    * [Add a new Chart of Account](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Add_a_new_Chart_of_Account)  * Quote Templates:    * [Get all Quote Templates](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_all_Quote_Templates)    * [Get a specific Quote Template](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_a_specific_Quote_Template)    * [Create a new Quote Template](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Create_a_new_Quote_Template)  * Connect Tax Engines:    * [Create a Connect Tax Engine](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Connect_Tax_Engines_Settings#Create_a_Connect_Tax_Engine)    * [Get a Connect Tax Engine](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Connect_Tax_Engines_Settings#Get_a_Connect_Tax_Engine)    * [Update a Connect Tax Engine](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Connect_Tax_Engines_Settings#Update_a_Connect_Tax_Engine)    * [Delete a Connect Tax Engine](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Connect_Tax_Engines_Settings#Delete_a_Connect_Tax_Engine)  * Custom Fields:    * [View all custom fields](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/View_all_custom_fields)    * [View custom fields of a specific object](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/View_custom_fields_of_a_specific_object)    * [Update custom fields of a specific object](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Update_custom_fields_of_a_specific_object)  * Units of Measure:    * [Create a Unit of Measure](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Create_a_Unit_of_Measure)    * [Get a Unit of Measure](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_a_Unit_of_Measure)    * [Get all Units of Measure](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Get_all_Units_of_Measure)    * [Update a Unit of Measure](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Update_a_Unit_of_Measure)    * [Delete a Unit of Measure](https://knowledgecenter.zuora.com/Central_Platform/API/BB_C_Settings_API/Settings_API_tutorials/Delete_a_Unit_of_Measure) 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.list_all_settings_response import ListAllSettingsResponse
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
    api_instance = zuora_sdk.SettingsApi(api_client)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    accept = 'accept_example' # str | Specifies response media type. If you omit the `Accept` header parameter, the response body is by default in JSON format. If you include `Accept` header parameter and set it to `application/csv`, the response body is in csv format. (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List all settings
        api_response = api_instance.get_list_all_settings(accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, accept=accept, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of SettingsApi->get_list_all_settings:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SettingsApi->get_list_all_settings: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **accept** | **str**| Specifies response media type. If you omit the &#x60;Accept&#x60; header parameter, the response body is by default in JSON format. If you include &#x60;Accept&#x60; header parameter and set it to &#x60;application/csv&#x60;, the response body is in csv format. | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**ListAllSettingsResponse**](ListAllSettingsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/csv, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_process_settings_batch_request**
> SettingsBatchResponse post_process_settings_batch_request(batch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Submit settings requests

Submit a batch of settings requests by this single API operation. nBy default, one batch settings request can contain a maximum of 100 single operation requests, including:  * All the single requests in the process batch settings request. * All the children requests of the single requests.  This maximum value is configurable. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.settings_batch_request import SettingsBatchRequest
from zuora_sdk.models.settings_batch_response import SettingsBatchResponse
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
    api_instance = zuora_sdk.SettingsApi(api_client)
    batch_request = zuora_sdk.SettingsBatchRequest() # SettingsBatchRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Submit settings requests
        api_response = api_instance.post_process_settings_batch_request(batch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of SettingsApi->post_process_settings_batch_request:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SettingsApi->post_process_settings_batch_request: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_request** | [**SettingsBatchRequest**](SettingsBatchRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**SettingsBatchResponse**](SettingsBatchResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

