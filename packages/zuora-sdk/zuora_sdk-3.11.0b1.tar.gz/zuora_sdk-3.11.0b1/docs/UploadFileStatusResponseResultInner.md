# UploadFileStatusResponseResultInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_log** | **str** |  | [optional] 
**file_request_id** | **int** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_status_response_result_inner import UploadFileStatusResponseResultInner

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileStatusResponseResultInner from a JSON string
upload_file_status_response_result_inner_instance = UploadFileStatusResponseResultInner.from_json(json)
# print the JSON string representation of the object
print(UploadFileStatusResponseResultInner.to_json())

# convert the object into a dict
upload_file_status_response_result_inner_dict = upload_file_status_response_result_inner_instance.to_dict()
# create an instance of UploadFileStatusResponseResultInner from a dict
upload_file_status_response_result_inner_from_dict = UploadFileStatusResponseResultInner.from_dict(upload_file_status_response_result_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


