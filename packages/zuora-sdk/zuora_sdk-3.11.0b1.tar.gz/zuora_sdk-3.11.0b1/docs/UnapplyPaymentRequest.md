# UnapplyPaymentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memos** | [**List[UnapplyPaymentDebitMemoApplication]**](UnapplyPaymentDebitMemoApplication.md) | Container for debit memos. The maximum number of debit memos is 1,000.  | [optional] 
**effective_date** | **str** | The date when the payment is unapplied, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**invoices** | [**List[UnapplyPaymentInvoiceApplication]**](UnapplyPaymentInvoiceApplication.md) | Container for invoices. The maximum number of invoice is 1,000.  | [optional] 

## Example

```python
from zuora_sdk.models.unapply_payment_request import UnapplyPaymentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyPaymentRequest from a JSON string
unapply_payment_request_instance = UnapplyPaymentRequest.from_json(json)
# print the JSON string representation of the object
print(UnapplyPaymentRequest.to_json())

# convert the object into a dict
unapply_payment_request_dict = unapply_payment_request_instance.to_dict()
# create an instance of UnapplyPaymentRequest from a dict
unapply_payment_request_from_dict = UnapplyPaymentRequest.from_dict(unapply_payment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


