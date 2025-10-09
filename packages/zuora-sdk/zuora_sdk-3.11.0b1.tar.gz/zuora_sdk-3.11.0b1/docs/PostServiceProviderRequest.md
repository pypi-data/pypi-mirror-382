# PostServiceProviderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the e-invoicing service provider.  | 
**test** | **bool** | Whether the e-invoicing service provider&#39;s configuration is intended for testing.   - If you set this field to &#x60;true&#x60;, requests are directed to the testing integration endpoints. If you set this field to &#x60;false&#x60;, requests are directed to the production integration endpoints.  | [optional] 
**provider** | **str** | The name of the e-invoicing service provider that can help you generate e-invoice files for billing documents.  | 
**company_identifier** | **str** | The Company Identifier is used to create a SenderSystemId, which serves to identify the system from which the transactions are sent.  | [optional] 
**api_key** | **str** | The API key is used to authenticate the e-invoicing service provider&#39;s requests.  | [optional] 
**secret_key** | **str** | The Secret Key is used to authenticate the e-invoicing service provider&#39;s requests.  | [optional] 
**client_certificate** | **str** | The client certificate is used to authenticate the e-invoicing service provider&#39;s requests, which should be in base64 encoded format.  | [optional] 
**client_certificate_type** | **str** | The client certificate type is used to specify the type of the client certificate. The default value is &#x60;PKCS12&#x60;.  | [optional] 
**client_certificate_password** | **str** | The client certificate password is the password to protect the client certificate.  | [optional] 

## Example

```python
from zuora_sdk.models.post_service_provider_request import PostServiceProviderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostServiceProviderRequest from a JSON string
post_service_provider_request_instance = PostServiceProviderRequest.from_json(json)
# print the JSON string representation of the object
print(PostServiceProviderRequest.to_json())

# convert the object into a dict
post_service_provider_request_dict = post_service_provider_request_instance.to_dict()
# create an instance of PostServiceProviderRequest from a dict
post_service_provider_request_from_dict = PostServiceProviderRequest.from_dict(post_service_provider_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


