# ReportListErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Response Status | [optional] [default to 'Invalid date format for 30-11-1993']
**status** | **str** | Error Status | [optional] [default to 'Error']

## Example

```python
from zuora_sdk.models.report_list_error_response import ReportListErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReportListErrorResponse from a JSON string
report_list_error_response_instance = ReportListErrorResponse.from_json(json)
# print the JSON string representation of the object
print(ReportListErrorResponse.to_json())

# convert the object into a dict
report_list_error_response_dict = report_list_error_response_instance.to_dict()
# create an instance of ReportListErrorResponse from a dict
report_list_error_response_from_dict = ReportListErrorResponse.from_dict(report_list_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


