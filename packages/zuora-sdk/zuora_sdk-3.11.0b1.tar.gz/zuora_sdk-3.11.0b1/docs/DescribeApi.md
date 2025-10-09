# zuora_sdk.DescribeApi

All URIs are relative to *https://rest.zuora.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_describe**](DescribeApi.md#get_describe) | **GET** /v1/describe/{object} | Describe an object


# **get_describe**
> str get_describe(object, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, show_currency_conversion_information=show_currency_conversion_information, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)

Describe an object

Provides a reference listing of each object that is available in your Zuora tenant.  The information returned by this call is useful if you are using [CRUD: Create Export](https://www.zuora.com/developer/api-references/api/operation/Object_PostExport) or the [AQuA API](https://knowledgecenter.zuora.com/DC_Developers/T_Aggregate_Query_API) to create a data source export. See [Export ZOQL](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL) for more information.  ### Response The response contains an XML document that lists the fields of the specified object. Each of the object's fields is represented by a `<field>` element in the XML document.      Each `<field>` element contains the following elements:  | Element      | Description                                                                                                                                                                                                                                                                                  | |--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| | `<name>`     | API name of the field.                                                                                                                                                                                                                                                                       | | `<label>`    | Name of the field in the Zuora user interface.                                                                                                                                                                                                                                               | | `<type>`     | Data type of the field. The possible data types are: `boolean`, `date`, `datetime`, `decimal`, `integer`, `picklist`, `text`, `timestamp`, and `ZOQL`. If the data type is `picklist`, the `<field>` element contains an `<options>` element that lists the possible values of the field.    | | `<contexts>` | Specifies the availability of the field. If the `<contexts>` element lists the `export` context, the field is available for use in data source exports.                                                                                                                                                |  The `<field>` element contains other elements that provide legacy information about the field. This information is not directly related to the REST API.  Response sample: ```xml <?xml version=\"1.0\" encoding=\"UTF-8\"?> <object>   <name>ProductRatePlanCharge</name>   <label>Product Rate Plan Charge</label>   <fields>     ...     <field>       <name>TaxMode</name>       <label>Tax Mode</label>       <type>picklist</type>       <options>         <option>TaxExclusive</option>         <option>TaxInclusive</option>       </options>       <contexts>         <context>export</context>       </contexts>       ...     </field>     ...   </fields> </object> ``` nIt is strongly recommended that your integration checks `<contexts>` elements in the response. If your integration does not check `<contexts>` elements, your integration may process fields that are not available for use in data source exports. See [Changes to the Describe API](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL/Changes_to_the_Describe_API) for more information. 

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
    api_instance = zuora_sdk.DescribeApi(api_client)
    object = 'object_example' # str | API name of an object in your Zuora tenant. For example, `InvoiceItem`. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects.
    accept_encoding = 'accept_encoding_example' # str | Include the `Accept-Encoding: gzip` header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a `Content-Encoding` header with the compression algorithm so that your client can decompress it.  (optional)
    content_encoding = 'content_encoding_example' # str | Include the `Content-Encoding: gzip` header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  (optional)
    authorization = 'authorization_example' # str | The value is in the `Bearer {token}` format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  (optional)
    zuora_track_id = 'zuora_track_id_example' # str | A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (`:`), semicolon (`;`), double quote (`\"`), and quote (`'`).  (optional)
    zuora_entity_ids = 'zuora_entity_ids_example' # str | An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  (optional)
    show_currency_conversion_information = 'show_currency_conversion_information_example' # str | Set the value to `yes` to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass `yes` to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text=Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. Set this parameter value to `no` to not include the additional currency conversion information in the result.  (optional)
    zuora_version = '2024-05-20' # str | The minor version of the Zuora REST API.   (optional) (default to '2024-05-20')
    zuora_org_ids = 'zuora_org_ids_example' # str | Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user's accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user's accessible orgs.  (optional)

    try:
        # Describe an object
        api_response = api_instance.get_describe(object, accept_encoding=accept_encoding, content_encoding=content_encoding, authorization=authorization, zuora_track_id=zuora_track_id, zuora_entity_ids=zuora_entity_ids, show_currency_conversion_information=show_currency_conversion_information, zuora_version=zuora_version, zuora_org_ids=zuora_org_ids)
        print("The response of DescribeApi->get_describe:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DescribeApi->get_describe: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object** | **str**| API name of an object in your Zuora tenant. For example, &#x60;InvoiceItem&#x60;. See [Zuora Object Model](https://www.zuora.com/developer/rest-api/general-concepts/object-model/) for the list of valid object names.  Depending on the features enabled in your Zuora tenant, you may not be able to list the fields of some objects. | 
 **accept_encoding** | **str**| Include the &#x60;Accept-Encoding: gzip&#x60; header to compress responses as a gzipped file. It can significantly reduce the bandwidth required for a response.   If specified, Zuora automatically compresses responses that contain over 1000 bytes of data, and the response contains a &#x60;Content-Encoding&#x60; header with the compression algorithm so that your client can decompress it.  | [optional] 
 **content_encoding** | **str**| Include the &#x60;Content-Encoding: gzip&#x60; header to compress a request. With this header specified, you should upload a gzipped file for the request payload instead of sending the JSON payload.  | [optional] 
 **authorization** | **str**| The value is in the &#x60;Bearer {token}&#x60; format where {token} is a valid OAuth token generated by calling [Create an OAuth token](https://www.zuora.com/developer/api-references/api/operation/createToken).  | [optional] 
 **zuora_track_id** | **str**| A custom identifier for tracing the API call. If you set a value for this header, Zuora returns the same value in the response headers. This header enables you to associate your system process identifiers with Zuora API calls, to assist with troubleshooting in the event of an issue.  The value of this field must use the US-ASCII character set and must not include any of the following characters: colon (&#x60;:&#x60;), semicolon (&#x60;;&#x60;), double quote (&#x60;\&quot;&#x60;), and quote (&#x60;&#39;&#x60;).  | [optional] 
 **zuora_entity_ids** | **str**| An entity ID. If you have [Zuora Multi-entity](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/Multi-entity) enabled and the OAuth token is valid for more than one entity, you must use this header to specify which entity to perform the operation in. If the OAuth token is only valid for a single entity, or you do not have Zuora Multi-entity enabled, you do not need to set this header.  | [optional] 
 **show_currency_conversion_information** | **str**| Set the value to &#x60;yes&#x60; to get additional currency conversion information in the result. **Notes:**  - When **Automatically include additional Currency Conversion information** in currency conversion settings is checked, you can pass &#x60;yes&#x60; to get additional fields in the result. See [Configure Foreign Currency Conversion](https://knowledgecenter.zuora.com/Zuora_Payments/Zuora_Finance/D_Finance_Settings/F_Foreign_Currency_Conversion#:~:text&#x3D;Automatically%20include%20additional%20Currency%20Conversion%20information%20in%20data%20source%20exports%3A%C2%A0Select%20this%20check%20box%20if%20you%20want%20to%20access%20foreign%20currency%20conversion%20data%20through%20data%20source%20exports.) to check the **Automatically include additional Currency Conversion information**. - By default if you need additional Currency Conversion information, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/hc/en-us\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;. Set this parameter value to &#x60;no&#x60; to not include the additional currency conversion information in the result.  | [optional] 
 **zuora_version** | **str**| The minor version of the Zuora REST API.   | [optional] [default to &#39;2024-05-20&#39;]
 **zuora_org_ids** | **str**| Comma separated IDs. If you have Zuora Multi-Org enabled, you can use this header to specify which orgs to perform the operation in. If you do not have Zuora Multi-Org enabled, you should not set this header. The IDs must be a sub-set of the user&#39;s accessible orgs. If you specify an org that the user does not have access to, the operation fails. If the header is not set, the operation is performed in scope of the user&#39;s accessible orgs.  | [optional] 

### Return type

**str**

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/xml; charset=utf-8, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Returns an XML document that lists the fields of the specified object  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**400** | Invalid input |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**401** |  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * WWW-Authenticate - The value of this header is:  &#x60;&#x60;&#x60; Basic realm&#x3D;Zuora API, ZSession realm&#x3D;Zuora API, Bearer realm&#x3D;Zuora API &#x60;&#x60;&#x60;  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**403** | Unauthorized |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |
**404** | Returns an XML document that indicates the error  |  * Content-Encoding -  <br>  * RateLimit-Limit -  <br>  * RateLimit-Remaining -  <br>  * RateLimit-Reset -  <br>  * Concurrency-Limit-Limit -  <br>  * Concurrency-Limit-Remaining -  <br>  * Concurrency-Limit-Type -  <br>  * Zuora-Request-Id -  <br>  * Zuora-Track-Id -  <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

