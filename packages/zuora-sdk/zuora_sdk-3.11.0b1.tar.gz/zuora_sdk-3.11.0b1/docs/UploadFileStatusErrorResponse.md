# UploadFileStatusErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] [default to 'Error']
**message** | **str** | Response message | [optional] [default to 'Job id is mandatory to poll the status']
**result** | **str** | Response result | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_status_error_response import UploadFileStatusErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileStatusErrorResponse from a JSON string
upload_file_status_error_response_instance = UploadFileStatusErrorResponse.from_json(json)
# print the JSON string representation of the object
print(UploadFileStatusErrorResponse.to_json())

# convert the object into a dict
upload_file_status_error_response_dict = upload_file_status_error_response_instance.to_dict()
# create an instance of UploadFileStatusErrorResponse from a dict
upload_file_status_error_response_from_dict = UploadFileStatusErrorResponse.from_dict(upload_file_status_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


