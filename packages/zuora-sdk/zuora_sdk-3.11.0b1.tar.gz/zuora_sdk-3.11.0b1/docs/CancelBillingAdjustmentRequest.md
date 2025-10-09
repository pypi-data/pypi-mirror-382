# CancelBillingAdjustmentRequest

Information about `CancelBillingAdjustment`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memo_custom_fields** | **Dict[str, object]** | Container for custom fields of the Debit Memo. The custom fields of the Debit Memo can be defined during Cancel Adjustment | [optional] 

## Example

```python
from zuora_sdk.models.cancel_billing_adjustment_request import CancelBillingAdjustmentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CancelBillingAdjustmentRequest from a JSON string
cancel_billing_adjustment_request_instance = CancelBillingAdjustmentRequest.from_json(json)
# print the JSON string representation of the object
print(CancelBillingAdjustmentRequest.to_json())

# convert the object into a dict
cancel_billing_adjustment_request_dict = cancel_billing_adjustment_request_instance.to_dict()
# create an instance of CancelBillingAdjustmentRequest from a dict
cancel_billing_adjustment_request_from_dict = CancelBillingAdjustmentRequest.from_dict(cancel_billing_adjustment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


