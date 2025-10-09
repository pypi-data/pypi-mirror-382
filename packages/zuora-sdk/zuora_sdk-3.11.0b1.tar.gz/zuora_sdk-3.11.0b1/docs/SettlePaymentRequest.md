# SettlePaymentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway_reconciliation_reason** | **str** | The reason of gateway reconciliation.  | [optional] 
**gateway_reconciliation_status** | **str** | The status of gateway reconciliation.  | [optional] 
**payout_id** | **str** | The payout ID from the gateway side.  | [optional] 
**settled_on** | **str** | The date and time of the transaction settlement. The format is &#x60;yyyy-mm-dd hh:mm:ss&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.settle_payment_request import SettlePaymentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettlePaymentRequest from a JSON string
settle_payment_request_instance = SettlePaymentRequest.from_json(json)
# print the JSON string representation of the object
print(SettlePaymentRequest.to_json())

# convert the object into a dict
settle_payment_request_dict = settle_payment_request_instance.to_dict()
# create an instance of SettlePaymentRequest from a dict
settle_payment_request_from_dict = SettlePaymentRequest.from_dict(settle_payment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


