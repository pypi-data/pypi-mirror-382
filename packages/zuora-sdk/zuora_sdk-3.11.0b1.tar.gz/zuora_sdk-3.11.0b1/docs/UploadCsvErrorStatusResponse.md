# UploadCsvErrorStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Error Response | [optional] [default to 'Error']
**message** | **str** | Error message | [optional] [default to 'No data found']
**result** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_csv_error_status_response import UploadCsvErrorStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvErrorStatusResponse from a JSON string
upload_csv_error_status_response_instance = UploadCsvErrorStatusResponse.from_json(json)
# print the JSON string representation of the object
print(UploadCsvErrorStatusResponse.to_json())

# convert the object into a dict
upload_csv_error_status_response_dict = upload_csv_error_status_response_instance.to_dict()
# create an instance of UploadCsvErrorStatusResponse from a dict
upload_csv_error_status_response_from_dict = UploadCsvErrorStatusResponse.from_dict(upload_csv_error_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


