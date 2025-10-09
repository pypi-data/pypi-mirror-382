# CreatePaymentDebitMemoApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment associated with the specific debit memo or taxation item. | 
**debit_memo_item_id** | **str** | The ID of the specific debit memo item.  | [optional] 
**tax_item_id** | **str** | The ID of the specific taxation item.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_debit_memo_application_item import CreatePaymentDebitMemoApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentDebitMemoApplicationItem from a JSON string
create_payment_debit_memo_application_item_instance = CreatePaymentDebitMemoApplicationItem.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentDebitMemoApplicationItem.to_json())

# convert the object into a dict
create_payment_debit_memo_application_item_dict = create_payment_debit_memo_application_item_instance.to_dict()
# create an instance of CreatePaymentDebitMemoApplicationItem from a dict
create_payment_debit_memo_application_item_from_dict = CreatePaymentDebitMemoApplicationItem.from_dict(create_payment_debit_memo_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


