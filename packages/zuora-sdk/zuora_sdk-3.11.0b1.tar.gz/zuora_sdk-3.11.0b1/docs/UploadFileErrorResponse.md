# UploadFileErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Error']
**message** | **str** | Response Message | [optional] [default to 'Exception occurred. Please contact Zuora Revenue Support']
**result** | [**UploadFileErrorResponseResult**](UploadFileErrorResponseResult.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_error_response import UploadFileErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileErrorResponse from a JSON string
upload_file_error_response_instance = UploadFileErrorResponse.from_json(json)
# print the JSON string representation of the object
print(UploadFileErrorResponse.to_json())

# convert the object into a dict
upload_file_error_response_dict = upload_file_error_response_instance.to_dict()
# create an instance of UploadFileErrorResponse from a dict
upload_file_error_response_from_dict = UploadFileErrorResponse.from_dict(upload_file_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


