# ReportDownloadErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Response Status | [optional] [default to 'File name does not exist in RevPro. Please check the file name.']
**result** | **str** | Response Status | [optional] 
**status** | **str** | Response Status | [optional] [default to 'Error']

## Example

```python
from zuora_sdk.models.report_download_error_response import ReportDownloadErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReportDownloadErrorResponse from a JSON string
report_download_error_response_instance = ReportDownloadErrorResponse.from_json(json)
# print the JSON string representation of the object
print(ReportDownloadErrorResponse.to_json())

# convert the object into a dict
report_download_error_response_dict = report_download_error_response_instance.to_dict()
# create an instance of ReportDownloadErrorResponse from a dict
report_download_error_response_from_dict = ReportDownloadErrorResponse.from_dict(report_download_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


