# ApplyPaymentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memos** | [**List[ApplyPaymentDebitMemoApplication]**](ApplyPaymentDebitMemoApplication.md) | Container for debit memos. The maximum number of debit memos is 1,000.  | [optional] 
**effective_date** | **str** | The date when the payment application takes effect, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**invoices** | [**List[ApplyPaymentInvoiceApplication]**](ApplyPaymentInvoiceApplication.md) | Container for invoices. The maximum number of invoices is 1,000.  | [optional] 

## Example

```python
from zuora_sdk.models.apply_payment_request import ApplyPaymentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyPaymentRequest from a JSON string
apply_payment_request_instance = ApplyPaymentRequest.from_json(json)
# print the JSON string representation of the object
print(ApplyPaymentRequest.to_json())

# convert the object into a dict
apply_payment_request_dict = apply_payment_request_instance.to_dict()
# create an instance of ApplyPaymentRequest from a dict
apply_payment_request_from_dict = ApplyPaymentRequest.from_dict(apply_payment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


