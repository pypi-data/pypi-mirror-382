# UploadFileErrorResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_request_id** | **int** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_error_response_result import UploadFileErrorResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileErrorResponseResult from a JSON string
upload_file_error_response_result_instance = UploadFileErrorResponseResult.from_json(json)
# print the JSON string representation of the object
print(UploadFileErrorResponseResult.to_json())

# convert the object into a dict
upload_file_error_response_result_dict = upload_file_error_response_result_instance.to_dict()
# create an instance of UploadFileErrorResponseResult from a dict
upload_file_error_response_result_from_dict = UploadFileErrorResponseResult.from_dict(upload_file_error_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


