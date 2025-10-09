# UploadCsvResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **int** |  | [optional] 
**id** | **str** |  | [optional] 
**message** | **str** |  | [optional] 
**status** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_csv_response_result import UploadCsvResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvResponseResult from a JSON string
upload_csv_response_result_instance = UploadCsvResponseResult.from_json(json)
# print the JSON string representation of the object
print(UploadCsvResponseResult.to_json())

# convert the object into a dict
upload_csv_response_result_dict = upload_csv_response_result_instance.to_dict()
# create an instance of UploadCsvResponseResult from a dict
upload_csv_response_result_from_dict = UploadCsvResponseResult.from_dict(upload_csv_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


