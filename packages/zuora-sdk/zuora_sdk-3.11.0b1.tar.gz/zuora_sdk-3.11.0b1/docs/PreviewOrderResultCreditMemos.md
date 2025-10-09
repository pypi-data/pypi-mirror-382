# PreviewOrderResultCreditMemos


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**credit_memo_items** | [**List[InvoiceItemPreviewResult]**](InvoiceItemPreviewResult.md) |  | [optional] 
**target_date** | **date** |  | [optional] 
**tax_amount** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_result_credit_memos import PreviewOrderResultCreditMemos

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderResultCreditMemos from a JSON string
preview_order_result_credit_memos_instance = PreviewOrderResultCreditMemos.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderResultCreditMemos.to_json())

# convert the object into a dict
preview_order_result_credit_memos_dict = preview_order_result_credit_memos_instance.to_dict()
# create an instance of PreviewOrderResultCreditMemos from a dict
preview_order_result_credit_memos_from_dict = PreviewOrderResultCreditMemos.from_dict(preview_order_result_credit_memos_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


