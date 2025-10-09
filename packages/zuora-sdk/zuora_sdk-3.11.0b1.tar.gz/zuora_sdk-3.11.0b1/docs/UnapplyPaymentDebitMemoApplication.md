# UnapplyPaymentDebitMemoApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment that is unapplied from the debit memo.  | 
**debit_memo_id** | **str** | The unique ID of the debit memo that the payment is unapplied from.  | [optional] 
**debit_memo_number** | **str** | The number of the debit memo that the payment is unapplied from.  | [optional] 
**items** | [**List[UnapplyPaymentDebitMemoApplicationItem]**](UnapplyPaymentDebitMemoApplicationItem.md) | Container for debit memo items. The maximum number of items is 1,000.   **Note:** This field is only available if you have the [Invoice Item Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/C_Invoice_Item_Settlement) feature enabled. Invoice Item Settlement must be used together with other Invoice Settlement features (Unapplied Payments, and Credit and Debit memos).  If you wish to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 

## Example

```python
from zuora_sdk.models.unapply_payment_debit_memo_application import UnapplyPaymentDebitMemoApplication

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyPaymentDebitMemoApplication from a JSON string
unapply_payment_debit_memo_application_instance = UnapplyPaymentDebitMemoApplication.from_json(json)
# print the JSON string representation of the object
print(UnapplyPaymentDebitMemoApplication.to_json())

# convert the object into a dict
unapply_payment_debit_memo_application_dict = unapply_payment_debit_memo_application_instance.to_dict()
# create an instance of UnapplyPaymentDebitMemoApplication from a dict
unapply_payment_debit_memo_application_from_dict = UnapplyPaymentDebitMemoApplication.from_dict(unapply_payment_debit_memo_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


