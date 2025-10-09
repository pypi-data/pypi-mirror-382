# UploadFileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **str** | The unique ID of the uploaded PDF file.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_response import UploadFileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileResponse from a JSON string
upload_file_response_instance = UploadFileResponse.from_json(json)
# print the JSON string representation of the object
print(UploadFileResponse.to_json())

# convert the object into a dict
upload_file_response_dict = upload_file_response_instance.to_dict()
# create an instance of UploadFileResponse from a dict
upload_file_response_from_dict = UploadFileResponse.from_dict(upload_file_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


