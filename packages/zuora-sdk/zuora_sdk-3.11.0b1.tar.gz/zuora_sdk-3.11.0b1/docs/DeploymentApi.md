# zuora_sdk.DeploymentApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**compare_and_deploy_product_catalog_template**](DeploymentApi.md#compare_and_deploy_product_catalog_template) | **POST** /deployment-manager/deployments/template/product_catalog | Compare and Deploy a template for product catalog to a target tenant
[**compare_and_deploy_product_catalog_tenant**](DeploymentApi.md#compare_and_deploy_product_catalog_tenant) | **POST** /deployment-manager/deployments/tenant/product_catalog | Compare and Deploy product catalog between a source tenant and a target tenant
[**compare_and_deploy_template**](DeploymentApi.md#compare_and_deploy_template) | **POST** /deployment-manager/deployments/templates | Compare and Deploy settings from a template to a target tenant
[**compare_and_deploy_tenant**](DeploymentApi.md#compare_and_deploy_tenant) | **POST** /deployment-manager/deployments/tenants | Compare and Deploy settings between a source tenant and a target tenant
[**retrieve_deployment**](DeploymentApi.md#retrieve_deployment) | **GET** /deployment-manager/deployments/{migrationId} | Retrieves a deployment log.
[**revert_deployment**](DeploymentApi.md#revert_deployment) | **POST** /deployment-manager/deployments/{migrationId}/revert | Reverts the deployment.


# **compare_and_deploy_product_catalog_template**
> DeploymentResponse compare_and_deploy_product_catalog_template(name, description, send_email, template, in_active_products, active_products, active_rate_plans, in_active_rate_plans, compare_field, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)

Compare and Deploy a template for product catalog to a target tenant

Compare and deploy a template for product catalog to a tenant.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.deployment_response import DeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    name = 'name_example' # str | Deployment's name.
    description = 'description_example' # str | Deployment's description.
    send_email = True # bool | Specifies if an email should be sent.
    template = None # bytearray | Template file.
    in_active_products = True # bool | Specifies if inactive products needs to be migrated.
    active_products = True # bool | Specifies if active products needs to be migrated.
    active_rate_plans = True # bool | Specifies if active rate plans needs to be migrated.
    in_active_rate_plans = True # bool | Specifies if inactive active rate plans needs to be migrated.
    compare_field = 'compare_field_example' # str | Specifies the compare field to be using during migration.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    emails = 'emails_example' # str | If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. (optional)
    comments = 'comments_example' # str | Content of the email to be sent. (optional)

    try:
        # Compare and Deploy a template for product catalog to a target tenant
        api_response = api_instance.compare_and_deploy_product_catalog_template(name, description, send_email, template, in_active_products, active_products, active_rate_plans, in_active_rate_plans, compare_field, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)
        print("The response of DeploymentApi->compare_and_deploy_product_catalog_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->compare_and_deploy_product_catalog_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Deployment&#39;s name. | 
 **description** | **str**| Deployment&#39;s description. | 
 **send_email** | **bool**| Specifies if an email should be sent. | 
 **template** | **bytearray**| Template file. | 
 **in_active_products** | **bool**| Specifies if inactive products needs to be migrated. | 
 **active_products** | **bool**| Specifies if active products needs to be migrated. | 
 **active_rate_plans** | **bool**| Specifies if active rate plans needs to be migrated. | 
 **in_active_rate_plans** | **bool**| Specifies if inactive active rate plans needs to be migrated. | 
 **compare_field** | **str**| Specifies the compare field to be using during migration. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **emails** | **str**| If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. | [optional] 
 **comments** | **str**| Content of the email to be sent. | [optional] 

### Return type

[**DeploymentResponse**](DeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully downloaded the template. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compare_and_deploy_product_catalog_tenant**
> DeploymentResponse compare_and_deploy_product_catalog_tenant(name, description, send_email, in_active_products, active_products, active_rate_plans, in_active_rate_plans, compare_field, source_tenant_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)

Compare and Deploy product catalog between a source tenant and a target tenant

Compare and deploy the product catalog of a tenant to a target tenant.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.deployment_response import DeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    name = 'name_example' # str | Deployment's name.
    description = 'description_example' # str | Deployment's description.
    send_email = True # bool | Specifies if an email should be sent.
    in_active_products = True # bool | Specifies if inactive products needs to be migrated.
    active_products = True # bool | Specifies if active products needs to be migrated.
    active_rate_plans = True # bool | Specifies if active rate plans needs to be migrated.
    in_active_rate_plans = True # bool | Specifies if inactive active rate plans needs to be migrated.
    compare_field = 'compare_field_example' # str | Specifies the compare field to be using during migration.
    source_tenant_id = 'source_tenant_id_example' # str | Id of the source tenant.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    emails = 'emails_example' # str | If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. (optional)
    comments = 'comments_example' # str | Content of the email to be sent. (optional)

    try:
        # Compare and Deploy product catalog between a source tenant and a target tenant
        api_response = api_instance.compare_and_deploy_product_catalog_tenant(name, description, send_email, in_active_products, active_products, active_rate_plans, in_active_rate_plans, compare_field, source_tenant_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)
        print("The response of DeploymentApi->compare_and_deploy_product_catalog_tenant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->compare_and_deploy_product_catalog_tenant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Deployment&#39;s name. | 
 **description** | **str**| Deployment&#39;s description. | 
 **send_email** | **bool**| Specifies if an email should be sent. | 
 **in_active_products** | **bool**| Specifies if inactive products needs to be migrated. | 
 **active_products** | **bool**| Specifies if active products needs to be migrated. | 
 **active_rate_plans** | **bool**| Specifies if active rate plans needs to be migrated. | 
 **in_active_rate_plans** | **bool**| Specifies if inactive active rate plans needs to be migrated. | 
 **compare_field** | **str**| Specifies the compare field to be using during migration. | 
 **source_tenant_id** | **str**| Id of the source tenant. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **emails** | **str**| If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. | [optional] 
 **comments** | **str**| Content of the email to be sent. | [optional] 

### Return type

[**DeploymentResponse**](DeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully downloaded the template. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compare_and_deploy_template**
> DeploymentResponse compare_and_deploy_template(name, description, send_email, template, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)

Compare and Deploy settings from a template to a target tenant

Compare and deploy a template to a tenant.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.deployment_response import DeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    name = 'name_example' # str | Deployment's name.
    description = 'description_example' # str | Deployment's description.
    send_email = True # bool | Specifies if an email should be sent.
    template = None # bytearray | Template contains the config metadata and target tenant information.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    emails = 'emails_example' # str | If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. (optional)
    comments = 'comments_example' # str | Content of the email to be sent. (optional)

    try:
        # Compare and Deploy settings from a template to a target tenant
        api_response = api_instance.compare_and_deploy_template(name, description, send_email, template, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments)
        print("The response of DeploymentApi->compare_and_deploy_template:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->compare_and_deploy_template: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Deployment&#39;s name. | 
 **description** | **str**| Deployment&#39;s description. | 
 **send_email** | **bool**| Specifies if an email should be sent. | 
 **template** | **bytearray**| Template contains the config metadata and target tenant information. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **emails** | **str**| If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. | [optional] 
 **comments** | **str**| Content of the email to be sent. | [optional] 

### Return type

[**DeploymentResponse**](DeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully downloaded the template. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **compare_and_deploy_tenant**
> DeploymentResponse compare_and_deploy_tenant(name, description, send_email, settings, notifications, workflows, custom_fields, product_catalog, user_roles, reporting, source_tenant_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments, custom_objects=custom_objects, taxation=taxation, billing_documents=billing_documents, custom_logic=custom_logic)

Compare and Deploy settings between a source tenant and a target tenant

Compare and deploy a source tenant to a target tenant.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.deployment_response import DeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    name = 'name_example' # str | Deployment's name.
    description = 'description_example' # str | Deployment's description.
    send_email = True # bool | Specifies if an email should be sent.
    settings = True # bool | Specified if settings module should be considered in the deployment process.
    notifications = True # bool | Specified if notifications module should be considered in the deployment process.
    workflows = True # bool | Specified if workflows module should be considered in the deployment process.
    custom_fields = True # bool | Specified if customFields module should be considered in the deployment process.
    product_catalog = True # bool | Specified if productCatalog module should be considered in the deployment process.
    user_roles = True # bool | Specified if userRoles module should be considered in the deployment process.
    reporting = True # bool | Specified if reporting module should be considered in the deployment process.
    source_tenant_id = 'source_tenant_id_example' # str | Id of the source tenant.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    emails = 'emails_example' # str | If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. (optional)
    comments = 'comments_example' # str | Content of the email to be sent. (optional)
    custom_objects = True # bool | Specified if customObjects module should be considered in the deployment process. (optional)
    taxation = True # bool | Specified if taxation module should be considered in the deployment process. (optional)
    billing_documents = True # bool | Specified if billingDocuments module should be considered in the deployment process. (optional)
    custom_logic = True # bool | Specified if customLogic module should be considered in the deployment process. (optional)

    try:
        # Compare and Deploy settings between a source tenant and a target tenant
        api_response = api_instance.compare_and_deploy_tenant(name, description, send_email, settings, notifications, workflows, custom_fields, product_catalog, user_roles, reporting, source_tenant_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, emails=emails, comments=comments, custom_objects=custom_objects, taxation=taxation, billing_documents=billing_documents, custom_logic=custom_logic)
        print("The response of DeploymentApi->compare_and_deploy_tenant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->compare_and_deploy_tenant: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Deployment&#39;s name. | 
 **description** | **str**| Deployment&#39;s description. | 
 **send_email** | **bool**| Specifies if an email should be sent. | 
 **settings** | **bool**| Specified if settings module should be considered in the deployment process. | 
 **notifications** | **bool**| Specified if notifications module should be considered in the deployment process. | 
 **workflows** | **bool**| Specified if workflows module should be considered in the deployment process. | 
 **custom_fields** | **bool**| Specified if customFields module should be considered in the deployment process. | 
 **product_catalog** | **bool**| Specified if productCatalog module should be considered in the deployment process. | 
 **user_roles** | **bool**| Specified if userRoles module should be considered in the deployment process. | 
 **reporting** | **bool**| Specified if reporting module should be considered in the deployment process. | 
 **source_tenant_id** | **str**| Id of the source tenant. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **emails** | **str**| If sendEmail parameter is set to true, comma separated values of emails can be specified. Example email1@test.com,email2@test.com. | [optional] 
 **comments** | **str**| Content of the email to be sent. | [optional] 
 **custom_objects** | **bool**| Specified if customObjects module should be considered in the deployment process. | [optional] 
 **taxation** | **bool**| Specified if taxation module should be considered in the deployment process. | [optional] 
 **billing_documents** | **bool**| Specified if billingDocuments module should be considered in the deployment process. | [optional] 
 **custom_logic** | **bool**| Specified if customLogic module should be considered in the deployment process. | [optional] 

### Return type

[**DeploymentResponse**](DeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully downloaded the template. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieve_deployment**
> RetrieveDeploymentResponse retrieve_deployment(migration_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids)

Retrieves a deployment log.

Retrieve a deployment log.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.retrieve_deployment_response import RetrieveDeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    migration_id = 'migration_id_example' # str | The unique ID of a migration.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)

    try:
        # Retrieves a deployment log.
        api_response = api_instance.retrieve_deployment(migration_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids)
        print("The response of DeploymentApi->retrieve_deployment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->retrieve_deployment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **migration_id** | **str**| The unique ID of a migration. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 

### Return type

[**RetrieveDeploymentResponse**](RetrieveDeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Retrieved the deployment log. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revert_deployment**
> RevertDeploymentResponse revert_deployment(migration_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids)

Reverts the deployment.

Revert a deployment.

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.revert_deployment_response import RevertDeploymentResponse
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
    api_instance = zuora_sdk.DeploymentApi(api_client)
    migration_id = 'migration_id_example' # str | The unique ID of a migration.
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)

    try:
        # Reverts the deployment.
        api_response = api_instance.revert_deployment(migration_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids)
        print("The response of DeploymentApi->revert_deployment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeploymentApi->revert_deployment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **migration_id** | **str**| The unique ID of a migration. | 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 

### Return type

[**RevertDeploymentResponse**](RevertDeploymentResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Reverted the deployment. |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Bad request |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

