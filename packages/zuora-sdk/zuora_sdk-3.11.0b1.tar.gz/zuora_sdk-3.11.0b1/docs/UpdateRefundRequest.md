# UpdateRefundRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the refund.  | [optional] 
**finance_information** | [**RefundRequestFinanceInformation**](RefundRequestFinanceInformation.md) |  | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code.  | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway. Use this field to reconcile refunds between your gateway and Zuora Payments.  You can only update the reference ID for external refunds.  | [optional] 
**gateway_reconciliation_status** | **str** |  | [optional] 
**gateway_reconciliation_reason** | **str** |  | [optional] 
**payout_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.update_refund_request import UpdateRefundRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateRefundRequest from a JSON string
update_refund_request_instance = UpdateRefundRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateRefundRequest.to_json())

# convert the object into a dict
update_refund_request_dict = update_refund_request_instance.to_dict()
# create an instance of UpdateRefundRequest from a dict
update_refund_request_from_dict = UpdateRefundRequest.from_dict(update_refund_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


