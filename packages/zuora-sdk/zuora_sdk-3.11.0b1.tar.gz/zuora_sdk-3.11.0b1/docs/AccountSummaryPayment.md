# AccountSummaryPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**effective_date** | **date** | Effective date as &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**id** | **str** | Payment ID.  | [optional] 
**paid_invoices** | [**List[AccountSummaryPaymentInvoice]**](AccountSummaryPaymentInvoice.md) | Container for paid invoices for this subscription.  | [optional] 
**payment_number** | **str** | Payment number.  | [optional] 
**payment_type** | **str** | Payment type; possible values are: &#x60;External&#x60;, &#x60;Electronic&#x60;.  | [optional] 
**status** | **str** | Payment status. Possible values are: &#x60;Draft&#x60;, &#x60;Processing&#x60;, &#x60;Processed&#x60;, &#x60;Error&#x60;, &#x60;Voided&#x60;, &#x60;Canceled&#x60;, &#x60;Posted&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_payment import AccountSummaryPayment

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryPayment from a JSON string
account_summary_payment_instance = AccountSummaryPayment.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryPayment.to_json())

# convert the object into a dict
account_summary_payment_dict = account_summary_payment_instance.to_dict()
# create an instance of AccountSummaryPayment from a dict
account_summary_payment_from_dict = AccountSummaryPayment.from_dict(account_summary_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


