# ServiceProviderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The ID of the e-invoicing service provider.  | [optional] 
**name** | **str** | The name of the e-invoicing service provider.  | [optional] 
**test** | **bool** | Whether the e-invoicing service provider&#39;s configuration is intended for testing.   - If you set this field to &#x60;true&#x60;, requests are directed to the testing integration endpoints. If you set this field to &#x60;false&#x60;, requests are directed to the production integration endpoints.  | [optional] 
**provider** | **str** | The name of the e-invoicing service provider that can help you generate e-invoice files for billing documents.  | [optional] 
**service_provider_number** | **str** | The unique number of the e-invoicing service provider.  | [optional] 
**company_identifier** | **str** | The Company Identifier is used to create a SenderSystemId, which serves to identify the system from which the transactions are sent.  | [optional] 
**api_key** | **str** | The API key is used to authenticate the e-invoicing service provider&#39;s requests.  | [optional] 
**client_certificate** | **str** | The client certificate is used to authenticate the e-invoicing service provider&#39;s requests, which should be in base64 encoded format.  | [optional] 
**client_certificate_type** | **str** | The client certificate type is used to authenticate the e-invoicing service provider&#39;s requests. The default value is &#x60;PKCS12&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.service_provider_response import ServiceProviderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceProviderResponse from a JSON string
service_provider_response_instance = ServiceProviderResponse.from_json(json)
# print the JSON string representation of the object
print(ServiceProviderResponse.to_json())

# convert the object into a dict
service_provider_response_dict = service_provider_response_instance.to_dict()
# create an instance of ServiceProviderResponse from a dict
service_provider_response_from_dict = ServiceProviderResponse.from_dict(service_provider_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


