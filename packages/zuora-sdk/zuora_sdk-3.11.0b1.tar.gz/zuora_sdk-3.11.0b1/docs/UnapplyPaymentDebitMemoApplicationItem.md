# UnapplyPaymentDebitMemoApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment that is unapplied from the specific debit mem or taxation item. | 
**debit_memo_item_id** | **str** | The ID of the specific debit memo item.  | [optional] 
**tax_item_id** | **str** | The ID of the specific taxation item.  | [optional] 

## Example

```python
from zuora_sdk.models.unapply_payment_debit_memo_application_item import UnapplyPaymentDebitMemoApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyPaymentDebitMemoApplicationItem from a JSON string
unapply_payment_debit_memo_application_item_instance = UnapplyPaymentDebitMemoApplicationItem.from_json(json)
# print the JSON string representation of the object
print(UnapplyPaymentDebitMemoApplicationItem.to_json())

# convert the object into a dict
unapply_payment_debit_memo_application_item_dict = unapply_payment_debit_memo_application_item_instance.to_dict()
# create an instance of UnapplyPaymentDebitMemoApplicationItem from a dict
unapply_payment_debit_memo_application_item_from_dict = UnapplyPaymentDebitMemoApplicationItem.from_dict(unapply_payment_debit_memo_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


