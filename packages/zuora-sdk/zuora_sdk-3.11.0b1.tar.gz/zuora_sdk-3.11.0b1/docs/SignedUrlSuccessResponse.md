# SignedUrlSuccessResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Response Status | [optional] 
**signed_url** | **str** | Signed s3 URL | [optional] [default to 'signed url']

## Example

```python
from zuora_sdk.models.signed_url_success_response import SignedUrlSuccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SignedUrlSuccessResponse from a JSON string
signed_url_success_response_instance = SignedUrlSuccessResponse.from_json(json)
# print the JSON string representation of the object
print(SignedUrlSuccessResponse.to_json())

# convert the object into a dict
signed_url_success_response_dict = signed_url_success_response_instance.to_dict()
# create an instance of SignedUrlSuccessResponse from a dict
signed_url_success_response_from_dict = SignedUrlSuccessResponse.from_dict(signed_url_success_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


