# ReportFileNotExistsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Response Status | [optional] [default to 'File name <filename> does not exist in RevPro']
**result** | **str** | Response Status | [optional] 
**status** | **str** | Response Status | [optional] [default to 'Error']

## Example

```python
from zuora_sdk.models.report_file_not_exists_response import ReportFileNotExistsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReportFileNotExistsResponse from a JSON string
report_file_not_exists_response_instance = ReportFileNotExistsResponse.from_json(json)
# print the JSON string representation of the object
print(ReportFileNotExistsResponse.to_json())

# convert the object into a dict
report_file_not_exists_response_dict = report_file_not_exists_response_instance.to_dict()
# create an instance of ReportFileNotExistsResponse from a dict
report_file_not_exists_response_from_dict = ReportFileNotExistsResponse.from_dict(report_file_not_exists_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


