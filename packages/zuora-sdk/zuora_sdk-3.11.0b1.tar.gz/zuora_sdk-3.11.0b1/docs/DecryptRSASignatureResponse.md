# DecryptRSASignatureResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**decrypted_signature** | **str** | The string of a list of the following items: Payment Pages 2.0 URL, tenant ID, timestamp,the Payment Page ID   The items are separated by &#39;#&#39;, e.g., \&quot;/apps/publichostedpagelite.do#12271#rvBp1AxBJwk6FrT7aqFuABIINiRbwJCc  #1418848373103#2c92c0f948f899\&quot; | [optional] 
**public_key** | **str** | The public key passed in as a request parameter.  | [optional] 
**signature** | **str** | The signature passed in as a request parameter.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.decrypt_rsa_signature_response import DecryptRSASignatureResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DecryptRSASignatureResponse from a JSON string
decrypt_rsa_signature_response_instance = DecryptRSASignatureResponse.from_json(json)
# print the JSON string representation of the object
print(DecryptRSASignatureResponse.to_json())

# convert the object into a dict
decrypt_rsa_signature_response_dict = decrypt_rsa_signature_response_instance.to_dict()
# create an instance of DecryptRSASignatureResponse from a dict
decrypt_rsa_signature_response_from_dict = DecryptRSASignatureResponse.from_dict(decrypt_rsa_signature_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


