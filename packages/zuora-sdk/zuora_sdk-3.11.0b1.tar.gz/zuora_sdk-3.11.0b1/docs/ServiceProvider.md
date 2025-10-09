# ServiceProvider


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
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
from zuora_sdk.models.service_provider import ServiceProvider

# TODO update the JSON string below
json = "{}"
# create an instance of ServiceProvider from a JSON string
service_provider_instance = ServiceProvider.from_json(json)
# print the JSON string representation of the object
print(ServiceProvider.to_json())

# convert the object into a dict
service_provider_dict = service_provider_instance.to_dict()
# create an instance of ServiceProvider from a dict
service_provider_from_dict = ServiceProvider.from_dict(service_provider_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


