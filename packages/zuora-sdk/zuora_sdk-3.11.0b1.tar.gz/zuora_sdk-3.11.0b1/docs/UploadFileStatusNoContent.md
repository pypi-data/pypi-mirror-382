# UploadFileStatusNoContent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response status | [optional] [default to 'Error']
**message** | **str** | Response message | [optional] [default to 'No records found matching the file Job id. Logs might have been truncated. Please contact Zuora Revenue support']
**result** | **List[object]** | Response result | [optional] 

## Example

```python
from zuora_sdk.models.upload_file_status_no_content import UploadFileStatusNoContent

# TODO update the JSON string below
json = "{}"
# create an instance of UploadFileStatusNoContent from a JSON string
upload_file_status_no_content_instance = UploadFileStatusNoContent.from_json(json)
# print the JSON string representation of the object
print(UploadFileStatusNoContent.to_json())

# convert the object into a dict
upload_file_status_no_content_dict = upload_file_status_no_content_instance.to_dict()
# create an instance of UploadFileStatusNoContent from a dict
upload_file_status_no_content_from_dict = UploadFileStatusNoContent.from_dict(upload_file_status_no_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


