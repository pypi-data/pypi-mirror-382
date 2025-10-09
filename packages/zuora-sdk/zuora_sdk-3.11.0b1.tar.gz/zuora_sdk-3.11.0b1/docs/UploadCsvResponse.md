# UploadCsvResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Success']
**message** | **str** | Response Message | [optional] [default to 'Data Staged in RevPro Successfully']
**result** | [**UploadCsvResponseResult**](UploadCsvResponseResult.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_csv_response import UploadCsvResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadCsvResponse from a JSON string
upload_csv_response_instance = UploadCsvResponse.from_json(json)
# print the JSON string representation of the object
print(UploadCsvResponse.to_json())

# convert the object into a dict
upload_csv_response_dict = upload_csv_response_instance.to_dict()
# create an instance of UploadCsvResponse from a dict
upload_csv_response_from_dict = UploadCsvResponse.from_dict(upload_csv_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


