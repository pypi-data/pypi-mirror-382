# ReportListResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Success']
**message** | **str** | Response Message | [optional] [default to '']
**result** | **List[Dict[str, str]]** |  | [optional] 

## Example

```python
from zuora_sdk.models.report_list_response import ReportListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReportListResponse from a JSON string
report_list_response_instance = ReportListResponse.from_json(json)
# print the JSON string representation of the object
print(ReportListResponse.to_json())

# convert the object into a dict
report_list_response_dict = report_list_response_instance.to_dict()
# create an instance of ReportListResponse from a dict
report_list_response_from_dict = ReportListResponse.from_dict(report_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


