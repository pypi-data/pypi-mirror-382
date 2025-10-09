# ReverseCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apply_effective_date** | **date** | The date when the to-be-reversed credit memo is applied to the newly generated debit memo, in &#x60;yyyy-mm-dd&#x60; format. The effective date must be later than or equal to the memo date.   The default value is the date when you reverse the credit memo and create the debit memo. | [optional] 
**comment** | **str** | Comments about the debit memo.  | [optional] 
**memo_date** | **date** | The date when the debit memo is created, in &#x60;yyyy-mm-dd&#x60; format. The memo date must be later than or equal to the credit memo&#39;s memo date.   The default value is the date when you reverse the credit memo and create the debit memo. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. The default value is &#x60;Credit memo reversal&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.reverse_credit_memo_request import ReverseCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseCreditMemoRequest from a JSON string
reverse_credit_memo_request_instance = ReverseCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(ReverseCreditMemoRequest.to_json())

# convert the object into a dict
reverse_credit_memo_request_dict = reverse_credit_memo_request_instance.to_dict()
# create an instance of ReverseCreditMemoRequest from a dict
reverse_credit_memo_request_from_dict = ReverseCreditMemoRequest.from_dict(reverse_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


