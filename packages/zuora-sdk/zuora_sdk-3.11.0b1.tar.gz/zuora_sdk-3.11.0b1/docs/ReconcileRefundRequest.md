# ReconcileRefundRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**ReconcileRefundRequestAction**](ReconcileRefundRequestAction.md) |  | 
**action_date** | **str** | The date and time of the refund reconciliation action, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**gateway_reconciliation_reason** | **str** | The reason of gateway reconciliation.  | [optional] 
**gateway_reconciliation_status** | **str** | The status of gateway reconciliation.  | 
**payout_id** | **str** | The payout ID of the refund from the gateway side.  | [optional] 

## Example

```python
from zuora_sdk.models.reconcile_refund_request import ReconcileRefundRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReconcileRefundRequest from a JSON string
reconcile_refund_request_instance = ReconcileRefundRequest.from_json(json)
# print the JSON string representation of the object
print(ReconcileRefundRequest.to_json())

# convert the object into a dict
reconcile_refund_request_dict = reconcile_refund_request_instance.to_dict()
# create an instance of ReconcileRefundRequest from a dict
reconcile_refund_request_from_dict = ReconcileRefundRequest.from_dict(reconcile_refund_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


