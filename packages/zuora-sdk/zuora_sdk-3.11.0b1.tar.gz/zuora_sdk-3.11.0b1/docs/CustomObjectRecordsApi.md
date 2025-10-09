# zuora_sdk.CustomObjectRecordsApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_custom_object_record_by_id**](CustomObjectRecordsApi.md#delete_custom_object_record_by_id) | **DELETE** /objects/records/default/{object}/{id} | Delete a custom object record
[**get_all_records_for_custom_object_type**](CustomObjectRecordsApi.md#get_all_records_for_custom_object_type) | **GET** /objects/records/default/{object} | List records for a custom object
[**get_custom_object_record_by_id**](CustomObjectRecordsApi.md#get_custom_object_record_by_id) | **GET** /objects/records/default/{object}/{id} | Retrieve a custom object record
[**patch_partial_update_custom_object_record**](CustomObjectRecordsApi.md#patch_partial_update_custom_object_record) | **PATCH** /objects/records/default/{object}/{id} | Partially update a custom object record
[**post_custom_object_records**](CustomObjectRecordsApi.md#post_custom_object_records) | **POST** /objects/records/default/{object} | Create custom object records
[**post_custom_object_records_batch_update_or_delete**](CustomObjectRecordsApi.md#post_custom_object_records_batch_update_or_delete) | **POST** /objects/batch/default/{object} | Update or delete custom object records
[**put_custom_object_record**](CustomObjectRecordsApi.md#put_custom_object_record) | **PUT** /objects/records/default/{object}/{id} | Update a custom object record


# **delete_custom_object_record_by_id**
> str delete_custom_object_record_by_id(object, id, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Delete a custom object record

Deletes a custom object record of the given type and ID.  Note that 200 response will be returned under either of the following conditions: * The record is identified and successfully deleted * The record could not be found nNote that the record is deleted immediately and, therefore, will not be retained upon successful deletion. 

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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    id = 'id_example' # str | Id identifier in uuid form
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Delete a custom object record
        api_response = api_instance.delete_custom_object_record_by_id(object, id, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->delete_custom_object_record_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->delete_custom_object_record_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **id** | **str**| Id identifier in uuid form | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

**str**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_records_for_custom_object_type**
> QueryCustomObjectRecordsResponse get_all_records_for_custom_object_type(object, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, q=q, ids=ids, page=page, page_size=page_size, cursor=cursor, zuora_org_ids=zuora_org_ids)

List records for a custom object

Lists all object records of the given type. You can also use the `q` query parameter to filter the output records.   ### Custom Objects read consistency  Custom Objects support eventually consistency. When you read custom object records, the response might not reflect the result of a recently completed operation and might include some stale data. The operations include creating, updating, and deleting custom object records.  If you repeat your read request after a short time, the response should return the latest data.  For example, if you create five records and perform a query that these five records satisfy the query conditions, there might be a delay before these records can be returned in the query result. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.query_custom_object_records_response import QueryCustomObjectRecordsResponse
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    q = 'q_example' # str | The query string to filter the records of a custom object. See the [Query syntax of custom object records](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Data_Model/Custom_object_records/Query_syntax_of_custom_object_records) for more information.  Note that the `q` parameter only applies to filterable fields. (optional)
    ids = 'ids_example' # str | UUIDs of the records to be queried. Each UUID must be a string of 36 characters. For example:  `GET /objects/records/default/passenger?ids=258d65b2-7bc6-4142-88bc-5184931af493&ids=82ecc9f7-b192-4f88-a4a3-4b2af6c750a1` (optional)
    page = 1 # int | The index number of the page that you want to retrieve. This parameter is dependent on `pageSize`. You must set `pageSize` before specifying `page`. For example, if you set `pageSize` to `20` and `page` to `2`, the 21st to 40th records are returned in the response.  (optional) (default to 1)
    page_size = 20 # int | The number of records returned per page in the response.  (optional) (default to 20)
    cursor = 'cursor_example' # str | The `cursor` points to the last record of the previous result set. The cursor record is not included in the query result. The call returns the first page if `cursor` is not provided and `pageSize` is valid. (optional)
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # List records for a custom object
        api_response = api_instance.get_all_records_for_custom_object_type(object, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, q=q, ids=ids, page=page, page_size=page_size, cursor=cursor, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->get_all_records_for_custom_object_type:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->get_all_records_for_custom_object_type: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **q** | **str**| The query string to filter the records of a custom object. See the [Query syntax of custom object records](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Data_Model/Custom_object_records/Query_syntax_of_custom_object_records) for more information.  Note that the &#x60;q&#x60; parameter only applies to filterable fields. | [optional] 
 **ids** | **str**| UUIDs of the records to be queried. Each UUID must be a string of 36 characters. For example:  &#x60;GET /objects/records/default/passenger?ids&#x3D;258d65b2-7bc6-4142-88bc-5184931af493&amp;ids&#x3D;82ecc9f7-b192-4f88-a4a3-4b2af6c750a1&#x60; | [optional] 
 **page** | **int**| The index number of the page that you want to retrieve. This parameter is dependent on &#x60;pageSize&#x60;. You must set &#x60;pageSize&#x60; before specifying &#x60;page&#x60;. For example, if you set &#x60;pageSize&#x60; to &#x60;20&#x60; and &#x60;page&#x60; to &#x60;2&#x60;, the 21st to 40th records are returned in the response.  | [optional] [default to 1]
 **page_size** | **int**| The number of records returned per page in the response.  | [optional] [default to 20]
 **cursor** | **str**| The &#x60;cursor&#x60; points to the last record of the previous result set. The cursor record is not included in the query result. The call returns the first page if &#x60;cursor&#x60; is not provided and &#x60;pageSize&#x60; is valid. | [optional] 
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**QueryCustomObjectRecordsResponse**](QueryCustomObjectRecordsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_custom_object_record_by_id**
> CustomObjectRecordWithAllFields get_custom_object_record_by_id(object, id, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Retrieve a custom object record

Retrieves a record of a given type by ID. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.custom_object_record_with_all_fields import CustomObjectRecordWithAllFields
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    id = 'id_example' # str | Id identifier in uuid form
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Retrieve a custom object record
        api_response = api_instance.get_custom_object_record_by_id(object, id, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->get_custom_object_record_by_id:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->get_custom_object_record_by_id: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **id** | **str**| Id identifier in uuid form | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CustomObjectRecordWithAllFields**](CustomObjectRecordWithAllFields.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**404** | Not exist |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patch_partial_update_custom_object_record**
> CustomObjectRecordWithAllFields patch_partial_update_custom_object_record(object, id, object_record_patch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Partially update a custom object record

Updates one or many fields of a custom object record. Patch update uses JSON Merge Patch as specified in [RFC 7386](https://tools.ietf.org/html/rfc7386). n### Limitations   * The storage of empty strings in records is not supported. * Null values must be formatted as the following example:    ```   {     \"records\": [       {         \"fieldName__c\": null       }     ]   }   ``` 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.custom_object_record_with_all_fields import CustomObjectRecordWithAllFields
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    id = 'id_example' # str | Id identifier in uuid form
    object_record_patch_request = None # Dict[str, object] | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Partially update a custom object record
        api_response = api_instance.patch_partial_update_custom_object_record(object, id, object_record_patch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->patch_partial_update_custom_object_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->patch_partial_update_custom_object_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **id** | **str**| Id identifier in uuid form | 
 **object_record_patch_request** | [**Dict[str, object]**](object.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CustomObjectRecordWithAllFields**](CustomObjectRecordWithAllFields.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/merge-patch+json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**404** | Object record does not exist |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_custom_object_records**
> PostCustomObjectRecordsResponse post_custom_object_records(object, custom_objects_records, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create custom object records

Creates custom object records with the given type.   Upon creating records of a custom object type, the 200 response contains a list of records that have been successfully processed and stored.   ### Limitations   This call has the following limitations: * The maximum number of records that you can create by one call is 1,000. * The storage of empty strings in records is not supported. * Null values must be formatted as the following example:    ```   {     \"records\": [       {         \"fieldName__c\": null       }     ]   }   ``` 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.post_custom_object_records_request import PostCustomObjectRecordsRequest
from zuora_sdk.models.post_custom_object_records_response import PostCustomObjectRecordsResponse
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    custom_objects_records = zuora_sdk.PostCustomObjectRecordsRequest() # PostCustomObjectRecordsRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create custom object records
        api_response = api_instance.post_custom_object_records(object, custom_objects_records, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->post_custom_object_records:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->post_custom_object_records: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **custom_objects_records** | [**PostCustomObjectRecordsRequest**](PostCustomObjectRecordsRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**PostCustomObjectRecordsResponse**](PostCustomObjectRecordsResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK  The 200 response indicates that the records have been partially or completely created.  * If the &#x60;allowPartialSuccess&#x60; flag is set to &#x60;false&#x60;, the 200 response indicates that all object records have been successfully created. * If the &#x60;allowPartialSuccess&#x60; flag is set to &#x60;true&#x60;, the 200 response indicates that some records might not be succesffully created and the error information might be contained in the response body.  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**500** | Internal error. Retry the returned records. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_custom_object_records_batch_update_or_delete**
> CustomObjectRecordsBatchUpdatePartialSuccessResponse post_custom_object_records_batch_update_or_delete(object, custom_object_record_batch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Update or delete custom object records

Makes a batch update or delete of custom object records. ### Limitations   This call has the following limitations: * The maximum number of records that you can update by one call is 1,000. * The maximum number of records that you can delete by one call is 1,000. * The storage of empty strings in records is not supported. * Null values must be formatted as the following example:    ```   {       \"action\": {           \"type\": \"update\",           \"records\": {               \"64edb2a5-2796-4e95-9559-846f8636a01b\": {                   \"fieldName__c\": null             }           }       }   }   ``` 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.custom_object_record_batch_request import CustomObjectRecordBatchRequest
from zuora_sdk.models.custom_object_records_batch_update_partial_success_response import CustomObjectRecordsBatchUpdatePartialSuccessResponse
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    custom_object_record_batch_request = zuora_sdk.CustomObjectRecordBatchRequest() # CustomObjectRecordBatchRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Update or delete custom object records
        api_response = api_instance.post_custom_object_records_batch_update_or_delete(object, custom_object_record_batch_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->post_custom_object_records_batch_update_or_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->post_custom_object_records_batch_update_or_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **custom_object_record_batch_request** | [**CustomObjectRecordBatchRequest**](CustomObjectRecordBatchRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CustomObjectRecordsBatchUpdatePartialSuccessResponse**](CustomObjectRecordsBatchUpdatePartialSuccessResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK  For the bacth &#x60;delete&#x60; action, it indicates the batch records have been successfully deleted.  For the batch &#x60;update&#x60; action, it indicates that the batch records have been partially or completely updated.  * If the &#x60;allowPartialSuccess&#x60; flag is set to &#x60;false&#x60;, the 200 response indicates that all object records have been successfully updated. * If the &#x60;allowPartialSuccess&#x60; flag is set to &#x60;true&#x60;, the 200 response indicates that some records might not be succesffully updated and the error information might be contained in the response body.  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Failed schema validation  For the batch &#x60;update&#x60; action, the 400 response only returns when the &#x60;allowPartialSuccess&#x60; flag is set to &#x60;false&#x60; and the batch records have failed schema validation.  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**500** | Internal error. Retry the returned records. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_custom_object_record**
> CustomObjectRecordWithAllFields put_custom_object_record(object, id, object_record_request, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, if_match=if_match, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Update a custom object record

Updates a record of the given type and ID.  ### Limitations   * The storage of empty strings in records is not supported. * Null values must be formatted as the following example:    ```   {     \"records\": [       {         \"fieldName__c\": null       }     ]   }   ``` 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.custom_object_record_with_all_fields import CustomObjectRecordWithAllFields
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
    api_instance = zuora_sdk.CustomObjectRecordsApi(api_client)
    object = 'object_example' # str | Specifies the custom object's API name as object. It is case-sensitive.
    id = 'id_example' # str | Id identifier in uuid form
    object_record_request = None # Dict[str, object] | 
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    if_match = 'if_match_example' # str | The expected ETag of the resource. You can use this header to perform a conditional request. Zuora responds with 412 Precondition Failed if the ETag of the resource does not match the value of this header.   (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Update a custom object record
        api_response = api_instance.put_custom_object_record(object, id, object_record_request, accept_encoding=accept_encoding, content_encoding=content_encoding, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, authorization=authorization, if_match=if_match, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of CustomObjectRecordsApi->put_custom_object_record:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomObjectRecordsApi->put_custom_object_record: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| Specifies the custom object&#39;s API name as object. It is case-sensitive. | 
 **id** | **str**| Id identifier in uuid form | 
 **object_record_request** | [**Dict[str, object]**](object.md)|  | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **if_match** | **str**| The expected ETag of the resource. You can use this header to perform a conditional request. Zuora responds with 412 Precondition Failed if the ETag of the resource does not match the value of this header.   | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**CustomObjectRecordWithAllFields**](CustomObjectRecordWithAllFields.md)

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
**404** | Object record does not exist |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

