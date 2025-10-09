# WriteOffResultTransaction

The credit memo apply information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_amount** | **float** | The credit memo applied amount. | [optional] 
**credit_memo_amount** | **float** | The credit memo amount. | [optional] 
**credit_memo_number** | **str** | The unique identification number of the credit memo. | [optional] 
**credit_memo_status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 
**debit_memo_number** | **str** | The unique identification number of the debit memo. | [optional] 
**invoice_number** | **str** | The unique identification number of the invoice. | [optional] 

## Example

```python
from zuora_sdk.models.write_off_result_transaction import WriteOffResultTransaction

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffResultTransaction from a JSON string
write_off_result_transaction_instance = WriteOffResultTransaction.from_json(json)
# print the JSON string representation of the object
print(WriteOffResultTransaction.to_json())

# convert the object into a dict
write_off_result_transaction_dict = write_off_result_transaction_instance.to_dict()
# create an instance of WriteOffResultTransaction from a dict
write_off_result_transaction_from_dict = WriteOffResultTransaction.from_dict(write_off_result_transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


