# RefundCreditMemoItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the refund on the specific item.  | 
**credit_memo_item_id** | **str** | The ID of the credit memo item that is refunded.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item that is refunded.  | [optional] 

## Example

```python
from zuora_sdk.models.refund_credit_memo_item_request import RefundCreditMemoItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RefundCreditMemoItemRequest from a JSON string
refund_credit_memo_item_request_instance = RefundCreditMemoItemRequest.from_json(json)
# print the JSON string representation of the object
print(RefundCreditMemoItemRequest.to_json())

# convert the object into a dict
refund_credit_memo_item_request_dict = refund_credit_memo_item_request_instance.to_dict()
# create an instance of RefundCreditMemoItemRequest from a dict
refund_credit_memo_item_request_from_dict = RefundCreditMemoItemRequest.from_dict(refund_credit_memo_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


