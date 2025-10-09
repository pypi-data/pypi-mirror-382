# ApplyPaymentDebitMemoApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount that is applied from the payment to the debit memo.  | 
**debit_memo_id** | **str** | The unique ID of the debit memo that the payment is applied to.  | [optional] 
**debit_memo_number** | **str** | The number of the debit memo that the payment is applied to.  | [optional] 
**items** | [**List[ApplyPaymentDebitMemoApplicationItem]**](ApplyPaymentDebitMemoApplicationItem.md) | Container for debit memo items. The maximum number of items is 1,000.  **Note:** This field is only available if you have the [Invoice Item Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/C_Invoice_Item_Settlement) feature enabled. Invoice Item Settlement must be used together with other Invoice Settlement features (Unapplied Payments, and Credit and Debit memos).  If you wish to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  | [optional] 

## Example

```python
from zuora_sdk.models.apply_payment_debit_memo_application import ApplyPaymentDebitMemoApplication

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyPaymentDebitMemoApplication from a JSON string
apply_payment_debit_memo_application_instance = ApplyPaymentDebitMemoApplication.from_json(json)
# print the JSON string representation of the object
print(ApplyPaymentDebitMemoApplication.to_json())

# convert the object into a dict
apply_payment_debit_memo_application_dict = apply_payment_debit_memo_application_instance.to_dict()
# create an instance of ApplyPaymentDebitMemoApplication from a dict
apply_payment_debit_memo_application_from_dict = ApplyPaymentDebitMemoApplication.from_dict(apply_payment_debit_memo_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


