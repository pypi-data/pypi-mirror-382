# UploadCsvStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Response | [optional] [default to 'Success']
**result** | [**UploadCsvStatusResponseResult**](UploadCsvStatusResponseResult.md) |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_csv_status_response import UploadCsvStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvStatusResponse from a JSON string
upload_csv_status_response_instance = UploadCsvStatusResponse.from_json(json)
# print the JSON string representation of the object
print(UploadCsvStatusResponse.to_json())

# convert the object into a dict
upload_csv_status_response_dict = upload_csv_status_response_instance.to_dict()
# create an instance of UploadCsvStatusResponse from a dict
upload_csv_status_response_from_dict = UploadCsvStatusResponse.from_dict(upload_csv_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


