# CollectDebitMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_order** | **List[str]** | The priority order to apply credit memos and/or unapplied payments to the debit memo. Possible item values are: &#x60;CreditMemo&#x60;, &#x60;UnappliedPayment&#x60;.   **Note:**   - This field is valid only if the &#x60;applyCredit&#x60; field is set to &#x60;true&#x60;.   - If no value is specified for this field, the default priority order is used, [\&quot;CreditMemo\&quot;, \&quot;UnappliedPayment\&quot;], to apply credit memos first and then apply unapplied payments.   - If only one item is specified, only the items of the spedified type are applied to invoices. For example, if the value is &#x60;[\&quot;CreditMemo\&quot;]&#x60;, only credit memos are used to apply the debit memo. | [optional] 
**apply_credit** | **bool** | Whether to automatically apply credit memos or unapplied payments, or both to the debit memo.  If the value is &#x60;true&#x60;, the credit memo or unapplied payment, or both will be automatically applied to the debit memo. If no value is specified or the value is &#x60;false&#x60;, no action is taken. | [optional] [default to False]
**collect** | **bool** | Indicates if the current request needs to collect payment or not.  | [optional] [default to False]
**payment** | [**CollectDebitMemoRequestPayment**](CollectDebitMemoRequestPayment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_request import CollectDebitMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoRequest from a JSON string
collect_debit_memo_request_instance = CollectDebitMemoRequest.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoRequest.to_json())

# convert the object into a dict
collect_debit_memo_request_dict = collect_debit_memo_request_instance.to_dict()
# create an instance of CollectDebitMemoRequest from a dict
collect_debit_memo_request_from_dict = CollectDebitMemoRequest.from_dict(collect_debit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


