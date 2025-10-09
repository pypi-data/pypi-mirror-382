# UploadUsageFileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**check_import_status** | **str** | The path for checking the status of the import.   The possible status values at this path are &#x60;Pending&#x60;, &#x60;Processing&#x60;, &#x60;Completed&#x60;, &#x60;Canceled&#x60;, and &#x60;Failed&#x60;. Only &#x60;Completed&#x60; indicates that the file contents were imported successfully. | [optional] 
**size** | **int** | The size of the uploaded file in bytes.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.upload_usage_file_response import UploadUsageFileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadUsageFileResponse from a JSON string
upload_usage_file_response_instance = UploadUsageFileResponse.from_json(json)
# print the JSON string representation of the object
print(UploadUsageFileResponse.to_json())

# convert the object into a dict
upload_usage_file_response_dict = upload_usage_file_response_instance.to_dict()
# create an instance of UploadUsageFileResponse from a dict
upload_usage_file_response_from_dict = UploadUsageFileResponse.from_dict(upload_usage_file_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


