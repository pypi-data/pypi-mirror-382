# CancelBillingAdjustmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**debit_memo_number** | **str** | The Debit Memo generated for the cancelled adjustment.         | [optional] 

## Example

```python
from zuora_sdk.models.cancel_billing_adjustment_response import CancelBillingAdjustmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelBillingAdjustmentResponse from a JSON string
cancel_billing_adjustment_response_instance = CancelBillingAdjustmentResponse.from_json(json)
# print the JSON string representation of the object
print(CancelBillingAdjustmentResponse.to_json())

# convert the object into a dict
cancel_billing_adjustment_response_dict = cancel_billing_adjustment_response_instance.to_dict()
# create an instance of CancelBillingAdjustmentResponse from a dict
cancel_billing_adjustment_response_from_dict = CancelBillingAdjustmentResponse.from_dict(cancel_billing_adjustment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


