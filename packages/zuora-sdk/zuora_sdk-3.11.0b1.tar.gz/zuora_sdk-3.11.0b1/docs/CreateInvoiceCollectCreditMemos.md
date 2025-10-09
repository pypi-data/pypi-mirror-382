# CreateInvoiceCollectCreditMemos


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the credit memo.  | [optional] 
**total_amount** | **decimal.Decimal** | The amount of the credit memo.  | [optional] 
**memo_number** | **str** | The unique identification number of the credit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_collect_credit_memos import CreateInvoiceCollectCreditMemos

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceCollectCreditMemos from a JSON string
create_invoice_collect_credit_memos_instance = CreateInvoiceCollectCreditMemos.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceCollectCreditMemos.to_json())

# convert the object into a dict
create_invoice_collect_credit_memos_dict = create_invoice_collect_credit_memos_instance.to_dict()
# create an instance of CreateInvoiceCollectCreditMemos from a dict
create_invoice_collect_credit_memos_from_dict = CreateInvoiceCollectCreditMemos.from_dict(create_invoice_collect_credit_memos_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


