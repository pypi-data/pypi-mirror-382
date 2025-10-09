# RSASignatureResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | Public key generated for this Payment Page.  | [optional] 
**signature** | **str** | Digital signature generated for this Payment Page.   If &#x60;signature&#x60; returns &#x60;null&#x60; but &#x60;token&#x60; is successfully returned, please limit the number of the fields in your request to make sure that the maximum length supported by the RSA signature algorithm is not exceeded. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**tenant_id** | **str** | ID of the Zuora tenant.  | [optional] 
**token** | **str** | Token generated for this Payment Page.  | [optional] 

## Example

```python
from zuora_sdk.models.rsa_signature_response import RSASignatureResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RSASignatureResponse from a JSON string
rsa_signature_response_instance = RSASignatureResponse.from_json(json)
# print the JSON string representation of the object
print(RSASignatureResponse.to_json())

# convert the object into a dict
rsa_signature_response_dict = rsa_signature_response_instance.to_dict()
# create an instance of RSASignatureResponse from a dict
rsa_signature_response_from_dict = RSASignatureResponse.from_dict(rsa_signature_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


