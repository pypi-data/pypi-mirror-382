# SignedUrlInvalidReportResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**result** | **str** | Response Status | [optional] 
**message** | **str** | Signed s3 URL | [optional] [default to 'signed url']
**status** | **str** | Response status | [optional] [default to 'Error']

## Example

```python
from zuora_sdk.models.signed_url_invalid_report_response import SignedUrlInvalidReportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SignedUrlInvalidReportResponse from a JSON string
signed_url_invalid_report_response_instance = SignedUrlInvalidReportResponse.from_json(json)
# print the JSON string representation of the object
print(SignedUrlInvalidReportResponse.to_json())

# convert the object into a dict
signed_url_invalid_report_response_dict = signed_url_invalid_report_response_instance.to_dict()
# create an instance of SignedUrlInvalidReportResponse from a dict
signed_url_invalid_report_response_from_dict = SignedUrlInvalidReportResponse.from_dict(signed_url_invalid_report_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


