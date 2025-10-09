# zuora_sdk.ActionsApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**action_post_create**](ActionsApi.md#action_post_create) | **POST** /v1/action/create | Create
[**action_post_delete**](ActionsApi.md#action_post_delete) | **POST** /v1/action/delete | Delete
[**action_post_query**](ActionsApi.md#action_post_query) | **POST** /v1/action/query | Query
[**action_postquery_more**](ActionsApi.md#action_postquery_more) | **POST** /v1/action/queryMore | QueryMore
[**action_postupdate**](ActionsApi.md#action_postupdate) | **POST** /v1/action/update | Update


# **action_post_create**
> List[SaveResult] action_post_create(create_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create

Use the create call to create one or more objects of a specific type. You can specify different types in different create calls, but each create call must apply to only one type of object.  ### Limitations   This call has the following limitations:  * A maximum of 50 objects are supported in a single call. * The Orders feature is not supported. * The Invoice Settlement feature is not supported. This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. * The default WSDL version for Actions is 79. To create objects according to a different WSDL version, set the `X-Zuora-WSDL-Version` header. To find out in which WSDL version a particular object or field was introduced, see [Zuora SOAP API Version History](https://knowledgecenter.zuora.com/DC_Developers/G_SOAP_API/Zuora_SOAP_API_Version_History). n ### How to use this call  You can create on an array of one or more zObjects. The fields you should specify can be found in the corresponding \"CRUD: Create an *zObject*\" operation. For example, to create one or multiple accounts, use the request fields in the [CRUD: Create an account](https://www.zuora.com/developer/api-references/older-api/operation/Object_PostAccount/) operation.  It returns an array of SaveResults sorted in the same order, indicating the success or failure of creating each object. The following information applies to this call:  * You cannot pass in null zObjects. * You can pass in a maximum of 50 zObjects at a time. * All objects must be of the same type.  #### Using Create and Subscribe Calls   Both the Create and Subscribe calls will create a new account. However, there are differences between the calls.  Use the create call to create an account independent of a subscription.  Use the subscribe call to create the account with the subscription and the initial payment information. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.proxy_actioncreate_request import ProxyActioncreateRequest
from zuora_sdk.models.save_result import SaveResult
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
    api_instance = zuora_sdk.ActionsApi(api_client)
    create_request = zuora_sdk.ProxyActioncreateRequest() # ProxyActioncreateRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    reject_unknown_fields = False # bool | Specifies whether the call fails if the request body contains unknown fields. With `rejectUnknownFields` set to `true`, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  ```json {     \"message\": \"Error - unrecognised fields\" } ```  By default, Zuora ignores unknown fields in the request body.  (optional) (default to False)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    x_zuora_wsdl_version = '79' # str | Zuora WSDL version number.  (optional) (default to '79')
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create
        api_response = api_instance.action_post_create(create_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of ActionsApi->action_post_create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsApi->action_post_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_request** | [**ProxyActioncreateRequest**](ProxyActioncreateRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **reject_unknown_fields** | **bool**| Specifies whether the call fails if the request body contains unknown fields. With &#x60;rejectUnknownFields&#x60; set to &#x60;true&#x60;, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Error - unrecognised fields\&quot; } &#x60;&#x60;&#x60;  By default, Zuora ignores unknown fields in the request body.  | [optional] [default to False]
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **x_zuora_wsdl_version** | **str**| Zuora WSDL version number.  | [optional] [default to &#39;79&#39;]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**List[SaveResult]**](SaveResult.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **action_post_delete**
> List[DeleteResult] action_post_delete(delete_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Delete

Deletes one or more objects of the same type. You can specify different types in different delete calls, but each delete call must apply only to one type of object.  The following information applies to this call:  * You will need to first determine the IDs for the objects you wish to delete. * You cannot pass in any null IDs. * All objects in a specific delete call must be of the same type.   ### Objects per Call 50 objects are supported in a single call. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.delete_result import DeleteResult
from zuora_sdk.models.proxy_actiondelete_request import ProxyActiondeleteRequest
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
    api_instance = zuora_sdk.ActionsApi(api_client)
    delete_request = zuora_sdk.ProxyActiondeleteRequest() # ProxyActiondeleteRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    reject_unknown_fields = False # bool | Specifies whether the call fails if the request body contains unknown fields. With `rejectUnknownFields` set to `true`, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  ```json {     \"message\": \"Error - unrecognised fields\" } ```  By default, Zuora ignores unknown fields in the request body.  (optional) (default to False)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    x_zuora_wsdl_version = '79' # str | Zuora WSDL version number.  (optional) (default to '79')
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Delete
        api_response = api_instance.action_post_delete(delete_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of ActionsApi->action_post_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsApi->action_post_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **delete_request** | [**ProxyActiondeleteRequest**](ProxyActiondeleteRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **reject_unknown_fields** | **bool**| Specifies whether the call fails if the request body contains unknown fields. With &#x60;rejectUnknownFields&#x60; set to &#x60;true&#x60;, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Error - unrecognised fields\&quot; } &#x60;&#x60;&#x60;  By default, Zuora ignores unknown fields in the request body.  | [optional] [default to False]
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **x_zuora_wsdl_version** | **str**| Zuora WSDL version number.  | [optional] [default to &#39;79&#39;]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**List[DeleteResult]**](DeleteResult.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **action_post_query**
> ProxyActionqueryResponse action_post_query(query_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Query

The query call sends a query expression by specifying the object to query, the fields to retrieve from that object, and any filters to determine whether a given object should be queried.   You can use [Zuora Object Query Language](https://knowledgecenter.zuora.com/DC_Developers/K_Zuora_Object_Query_Language) (ZOQL) to construct those queries, passing them through the `queryString`. n Once the call is made, the API executes the query against the specified object and returns a query response object to your application. Your application can then iterate through rows in the query response to retrieve information.  ### Limitations   This call has the following limitations:  * All [ZOQL limitations](https://knowledgecenter.zuora.com/Central_Platform/Query/ZOQL#ZOQL_Limitations) apply. * All ZOQL keywords must be in lower case. * The number of records returned is limited to 2000 records. * The Invoice Settlement feature is not supported. This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. * The Orders feature is not supported, which means that the objects listed in [Orders Object Model](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/BA_Orders_Object_Model) are not supported. * The Active Rating feature is not supported. * The default WSDL version for Actions is 79. To query objects or fields according to a different WSDL version, set the `X-Zuora-WSDL-Version` header. To find out in which WSDL version a particular object or field was introduced, see [Zuora SOAP API Version History](https://knowledgecenter.zuora.com/DC_Developers/G_SOAP_API/Zuora_SOAP_API_Version_History). 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.proxy_actionquery_request import ProxyActionqueryRequest
from zuora_sdk.models.proxy_actionquery_response import ProxyActionqueryResponse
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
    api_instance = zuora_sdk.ActionsApi(api_client)
    query_request = zuora_sdk.ProxyActionqueryRequest() # ProxyActionqueryRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    reject_unknown_fields = False # bool | Specifies whether the call fails if the request body contains unknown fields. With `rejectUnknownFields` set to `true`, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  ```json {     \"message\": \"Error - unrecognised fields\" } ```  By default, Zuora ignores unknown fields in the request body.  (optional) (default to False)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    x_zuora_wsdl_version = '79' # str | Zuora WSDL version number.  (optional) (default to '79')
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Query
        api_response = api_instance.action_post_query(query_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of ActionsApi->action_post_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsApi->action_post_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**ProxyActionqueryRequest**](ProxyActionqueryRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **reject_unknown_fields** | **bool**| Specifies whether the call fails if the request body contains unknown fields. With &#x60;rejectUnknownFields&#x60; set to &#x60;true&#x60;, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Error - unrecognised fields\&quot; } &#x60;&#x60;&#x60;  By default, Zuora ignores unknown fields in the request body.  | [optional] [default to False]
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **x_zuora_wsdl_version** | **str**| Zuora WSDL version number.  | [optional] [default to &#39;79&#39;]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**ProxyActionqueryResponse**](ProxyActionqueryResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **action_postquery_more**
> ProxyActionqueryMoreResponse action_postquery_more(query_more_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

QueryMore

Use queryMore to request additional results from a previous query call. If your initial query call returns more than 2000 results, you can use queryMore to query for the additional results.   Any `queryLocator` results greater than 2,000, will only be stored by Zuora for 5 days before it is deleted. n  This call sends a request for additional results from an initial query call. If the initial query call returns more than 2000 results, you can use the `queryLocator` returned from query to request the next set of results.   **Note:** Zuora expires queryMore cursors after 15 minutes of activity.   To use queryMore, you first construct a query call. By default, the query call will return up to 2000 results. If there are more than 2000 results, query will return a boolean `done`, which will be marked as `false`, and a `queryLocator`, which is a marker you will pass to queryMore to get the next set of results. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.proxy_actionquery_more_request import ProxyActionqueryMoreRequest
from zuora_sdk.models.proxy_actionquery_more_response import ProxyActionqueryMoreResponse
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
    api_instance = zuora_sdk.ActionsApi(api_client)
    query_more_request = zuora_sdk.ProxyActionqueryMoreRequest() # ProxyActionqueryMoreRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    reject_unknown_fields = False # bool | Specifies whether the call fails if the request body contains unknown fields. With `rejectUnknownFields` set to `true`, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  ```json {     \"message\": \"Error - unrecognised fields\" } ```  By default, Zuora ignores unknown fields in the request body.  (optional) (default to False)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    x_zuora_wsdl_version = '79' # str | Zuora WSDL version number.  (optional) (default to '79')
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # QueryMore
        api_response = api_instance.action_postquery_more(query_more_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of ActionsApi->action_postquery_more:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsApi->action_postquery_more: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_more_request** | [**ProxyActionqueryMoreRequest**](ProxyActionqueryMoreRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **reject_unknown_fields** | **bool**| Specifies whether the call fails if the request body contains unknown fields. With &#x60;rejectUnknownFields&#x60; set to &#x60;true&#x60;, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Error - unrecognised fields\&quot; } &#x60;&#x60;&#x60;  By default, Zuora ignores unknown fields in the request body.  | [optional] [default to False]
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **x_zuora_wsdl_version** | **str**| Zuora WSDL version number.  | [optional] [default to &#39;79&#39;]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**ProxyActionqueryMoreResponse**](ProxyActionqueryMoreResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **action_postupdate**
> List[SaveResult] action_postupdate(update_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Update

 Updates the information in one or more objects of the same type. You can specify different types of objects in different update calls, but each specific update call must apply to only one type of object.   ### Limitations   This call has the following limitations:  * A maximum of 50 objects are supported in a single call. * The Invoice Settlement feature is not supported. This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. * The default WSDL version for Actions is 79. To update objects or fields according to a different WSDL version, set the `X-Zuora-WSDL-Version` header. To find out in which WSDL version a particular object or field was introduced, see [Zuora SOAP API Version History](https://knowledgecenter.zuora.com/DC_Developers/G_SOAP_API/Zuora_SOAP_API_Version_History). n ### How to use this call?   You can update an array of one or more zObjects. The fields you should specify can be found in the corresponding \"CRUD: Update an *zObject*\" operation. For example, to update one or multiple accounts, use the request fields in the [CRUD: Update an account](https://www.zuora.com/developer/api-references/older-api/operation/Object_PutAccount/) operation.  It returns an array of SaveResults sorted in the same order, indicating the success or failure of updating each object. The following information applies to this call:  * You cannot pass in null zObjects. * You can pass in a maximum of 50 zObjects at a time. * All objects must be of the same type. * For each field in each object, you must determine that object's ID. Then populate the fields that you want update with the new information. * Zuora ignores unrecognized fields in update calls. For example, if an optional field is spelled incorrectly or a field that does not exist is specified, Zuora ignores the field and continues to process the call. No error message is returned for unrecognized fields. 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.proxy_actionupdate_request import ProxyActionupdateRequest
from zuora_sdk.models.save_result import SaveResult
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
    api_instance = zuora_sdk.ActionsApi(api_client)
    update_request = zuora_sdk.ProxyActionupdateRequest() # ProxyActionupdateRequest | 
    idempotency_key = 'idempotency_key_example' # str | Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    reject_unknown_fields = False # bool | Specifies whether the call fails if the request body contains unknown fields. With `rejectUnknownFields` set to `true`, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  ```json {     \"message\": \"Error - unrecognised fields\" } ```  By default, Zuora ignores unknown fields in the request body.  (optional) (default to False)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    x_zuora_wsdl_version = '79' # str | Zuora WSDL version number.  (optional) (default to '79')
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Update
        api_response = api_instance.action_postupdate(update_request, idempotency_key=idempotency_key, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, reject_unknown_fields=reject_unknown_fields, zuora_entity_ids=zuora_entity_ids, zuora_track_id=zuora_track_id, x_zuora_wsdl_version=x_zuora_wsdl_version, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of ActionsApi->action_postupdate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ActionsApi->action_postupdate: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **update_request** | [**ProxyActionupdateRequest**](ProxyActionupdateRequest.md)|  | 
 **idempotency_key** | **str**| Specify a unique idempotency key if you want to perform an idempotent POST or PATCH request. Do not use this header in other request types.   With this header specified, the Zuora server can identify subsequent retries of the same request using this value, which prevents the same operation from being performed multiple times by accident.   | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **reject_unknown_fields** | **bool**| Specifies whether the call fails if the request body contains unknown fields. With &#x60;rejectUnknownFields&#x60; set to &#x60;true&#x60;, Zuora returns a 400 response if the request body contains unknown fields. The body of the 400 response is:  &#x60;&#x60;&#x60;json {     \&quot;message\&quot;: \&quot;Error - unrecognised fields\&quot; } &#x60;&#x60;&#x60;  By default, Zuora ignores unknown fields in the request body.  | [optional] [default to False]
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **x_zuora_wsdl_version** | **str**| Zuora WSDL version number.  | [optional] [default to &#39;79&#39;]
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**List[SaveResult]**](SaveResult.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

