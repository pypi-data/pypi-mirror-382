# AccountSummaryInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | Invoice amount before adjustments, discounts, and similar items.  | [optional] 
**balance** | **float** | Balance due on the invoice.  | [optional] 
**due_date** | **date** | Due date as &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**id** | **str** | Invoice ID.  | [optional] 
**invoice_date** | **date** | Invoice date as &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**invoice_number** | **str** | Invoice number.  | [optional] 
**status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_invoice import AccountSummaryInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryInvoice from a JSON string
account_summary_invoice_instance = AccountSummaryInvoice.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryInvoice.to_json())

# convert the object into a dict
account_summary_invoice_dict = account_summary_invoice_instance.to_dict()
# create an instance of AccountSummaryInvoice from a dict
account_summary_invoice_from_dict = AccountSummaryInvoice.from_dict(account_summary_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


