# UploadCsvErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Error Response | [optional] [default to 'Error']
**message** | **str** | Error Message | [optional] [default to 'Error loading Data into RevPro Stage']
**result** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_csv_error_response import UploadCsvErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvErrorResponse from a JSON string
upload_csv_error_response_instance = UploadCsvErrorResponse.from_json(json)
# print the JSON string representation of the object
print(UploadCsvErrorResponse.to_json())

# convert the object into a dict
upload_csv_error_response_dict = upload_csv_error_response_instance.to_dict()
# create an instance of UploadCsvErrorResponse from a dict
upload_csv_error_response_from_dict = UploadCsvErrorResponse.from_dict(upload_csv_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


