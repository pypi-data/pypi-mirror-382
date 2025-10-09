# UploadRevenueFileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Response Status | [optional] [default to 'Success']
**message** | **str** | Response Message | [optional] [default to 'File consumed successfully by Revpro']
**result** | [**UploadRevenueFileResponseResult**](UploadRevenueFileResponseResult.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_revenue_file_response import UploadRevenueFileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UploadRevenueFileResponse from a JSON string
upload_revenue_file_response_instance = UploadRevenueFileResponse.from_json(json)
# print the JSON string representation of the object
print(UploadRevenueFileResponse.to_json())

# convert the object into a dict
upload_revenue_file_response_dict = upload_revenue_file_response_instance.to_dict()
# create an instance of UploadRevenueFileResponse from a dict
upload_revenue_file_response_from_dict = UploadRevenueFileResponse.from_dict(upload_revenue_file_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


