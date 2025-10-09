# UploadRevenueFileResponseResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_request_id** | **int** |  | [optional] 
**file_name** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upload_revenue_file_response_result import UploadRevenueFileResponseResult

# TODO update the JSON string below
json = "{}"
# create an instance of UploadRevenueFileResponseResult from a JSON string
upload_revenue_file_response_result_instance = UploadRevenueFileResponseResult.from_json(json)
# print the JSON string representation of the object
print(UploadRevenueFileResponseResult.to_json())

# convert the object into a dict
upload_revenue_file_response_result_dict = upload_revenue_file_response_result_instance.to_dict()
# create an instance of UploadRevenueFileResponseResult from a dict
upload_revenue_file_response_result_from_dict = UploadRevenueFileResponseResult.from_dict(upload_revenue_file_response_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


