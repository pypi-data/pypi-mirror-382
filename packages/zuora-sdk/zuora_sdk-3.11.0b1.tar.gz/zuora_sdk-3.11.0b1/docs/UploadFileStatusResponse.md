# UploadFileStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Success']
**message** | **str** | Response Message | [optional] [default to '']
**result** | [**List[UploadFileStatusResponseResultInner]**](UploadFileStatusResponseResultInner.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_status_response import UploadFileStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileStatusResponse from a JSON string
upload_file_status_response_instance = UploadFileStatusResponse.from_json(json)
# print the JSON string representation of the object
print(UploadFileStatusResponse.to_json())

# convert the object into a dict
upload_file_status_response_dict = upload_file_status_response_instance.to_dict()
# create an instance of UploadFileStatusResponse from a dict
upload_file_status_response_from_dict = UploadFileStatusResponse.from_dict(upload_file_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


