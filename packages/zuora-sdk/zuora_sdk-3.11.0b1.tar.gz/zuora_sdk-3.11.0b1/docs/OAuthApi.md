# zuora_sdk.OAuthApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_token**](OAuthApi.md#create_token) | **POST** /oauth/token | Create an OAuth token


# **create_token**
> TokenResponse create_token(client_id, client_secret, grant_type, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Create an OAuth token

Creates a bearer token that enables an OAuth client to authenticate with the Zuora REST API. The OAuth client must have been created using the Zuora UI. See [Authentication](https://www.zuora.com/developer/rest-api/general-concepts/authentication/) for more information.  **Note:** When using this operation, do not set any authentication headers such as `Authorization`, `apiAccessKeyId`, or `apiSecretAccessKey`.  You should not use this operation to generate a large number of bearer tokens in a short period of time; each token should be used until it expires. If you receive a 429 Too Many Requests response when using this operation, reduce the frequency of requests. This endpoint is rate limited by IP address.  For the rate limit information of authentication, see [Rate and concurrent request limits](https://www.zuora.com/developer/rest-api/general-concepts/rate-concurrency-limits/). 

### Example

* Bearer Authentication (bearerAuth):

```python
import zuora_sdk
from zuora_sdk.models.token_response import TokenResponse
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
    api_instance = zuora_sdk.OAuthApi(api_client)
    client_id = 'client_id_example' # str | The Client ID of the OAuth client. 
    client_secret = 'client_secret_example' # str | The Client Secret that was displayed when the OAuth client was created. 
    grant_type = zuora_sdk.CreateTokenRequestGrantType() # CreateTokenRequestGrantType | 
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Create an OAuth token
        api_response = api_instance.create_token(client_id, client_secret, grant_type, zuora_track_id=zuora_track_id, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of OAuthApi->create_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OAuthApi->create_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **client_id** | **str**| The Client ID of the OAuth client.  | 
 **client_secret** | **str**| The Client Secret that was displayed when the OAuth client was created.  | 
 **grant_type** | **CreateTokenRequestGrantType**|  | 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

[**TokenResponse**](TokenResponse.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  * X-RateLimit-Limit-minute - The rate limit of this operation, in requests per minute. See [rate limits](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Policies/Concurrent_Request_Limits#Rate_limits) for more information.  <br>  * X-RateLimit-Remaining-minute - The number of requests that you may make in the next minute. See [rate limits](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Policies/Concurrent_Request_Limits#Rate_limits) for more information.  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**429** | Too Many Requests |  * X-RateLimit-Limit-minute - The rate limit of this operation, in requests per minute. See [rate limits](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Policies/Concurrent_Request_Limits#Rate_limits) for more information.  <br>  * X-RateLimit-Remaining-minute - The number of requests that you may make in the next minute. See [rate limits](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Policies/Concurrent_Request_Limits#Rate_limits) for more information.  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

