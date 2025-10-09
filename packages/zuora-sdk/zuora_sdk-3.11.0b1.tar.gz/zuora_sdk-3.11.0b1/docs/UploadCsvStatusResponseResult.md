# UploadCsvStatusResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**message** | **str** |  | [optional] [default to 'Data Received']
**status** | **str** |  | [optional] [default to 'Successfully Uploaded']

## Example

```python
from zuora_sdk.models.upload_csv_status_response_result import UploadCsvStatusResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvStatusResponseResult from a JSON string
upload_csv_status_response_result_instance = UploadCsvStatusResponseResult.from_json(json)
# print the JSON string representation of the object
print(UploadCsvStatusResponseResult.to_json())

# convert the object into a dict
upload_csv_status_response_result_dict = upload_csv_status_response_result_instance.to_dict()
# create an instance of UploadCsvStatusResponseResult from a dict
upload_csv_status_response_result_from_dict = UploadCsvStatusResponseResult.from_dict(upload_csv_status_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


