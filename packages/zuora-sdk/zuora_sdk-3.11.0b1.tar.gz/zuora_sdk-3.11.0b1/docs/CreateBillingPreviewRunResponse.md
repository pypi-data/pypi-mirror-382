# CreateBillingPreviewRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | The request ID of this process.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**billing_preview_run_id** | **str** | Id of the billing preview run.  | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_preview_run_response import CreateBillingPreviewRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingPreviewRunResponse from a JSON string
create_billing_preview_run_response_instance = CreateBillingPreviewRunResponse.from_json(json)
# print the JSON string representation of the object
print(CreateBillingPreviewRunResponse.to_json())

# convert the object into a dict
create_billing_preview_run_response_dict = create_billing_preview_run_response_instance.to_dict()
# create an instance of CreateBillingPreviewRunResponse from a dict
create_billing_preview_run_response_from_dict = CreateBillingPreviewRunResponse.from_dict(create_billing_preview_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


