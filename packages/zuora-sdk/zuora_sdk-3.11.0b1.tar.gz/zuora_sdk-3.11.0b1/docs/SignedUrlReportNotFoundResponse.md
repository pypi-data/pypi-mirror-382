# SignedUrlReportNotFoundResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** | Error Response | [optional] 
**success** | **bool** | Success flag | [optional] [default to False]

## Example

```python
from zuora_sdk.models.signed_url_report_not_found_response import SignedUrlReportNotFoundResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SignedUrlReportNotFoundResponse from a JSON string
signed_url_report_not_found_response_instance = SignedUrlReportNotFoundResponse.from_json(json)
# print the JSON string representation of the object
print(SignedUrlReportNotFoundResponse.to_json())

# convert the object into a dict
signed_url_report_not_found_response_dict = signed_url_report_not_found_response_instance.to_dict()
# create an instance of SignedUrlReportNotFoundResponse from a dict
signed_url_report_not_found_response_from_dict = SignedUrlReportNotFoundResponse.from_dict(signed_url_report_not_found_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


