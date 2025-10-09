# AccountMetrics

Container for account metrics. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**balance** | **float** | The customer&#39;s total invoice balance minus credit balance.  | [optional] 
**currency** | **str** | The currency that metrics are aggregated based on.  | [optional] 
**contracted_mrr** | **float** | Future expected MRR that accounts for future upgrades, downgrades, upsells and cancellations. | [optional] 
**credit_balance** | **float** | Current credit balance. | [optional] 
**reserved_payment_amount** | **float** | The Reserved Payment Amount of the customer account. | [optional] 
**total_debit_memo_balance** | **float** | Total balance of all posted debit memos. | [optional] 
**total_invoice_balance** | **float** | Total balance of all posted invoices.  | [optional] 
**unapplied_credit_memo_amount** | **float** |  | [optional] 
**unapplied_payment_amount** | **float** | Total unapplied amount of all posted payments. | [optional] 

## Example

```python
from zuora_sdk.models.account_metrics import AccountMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of AccountMetrics from a JSON string
account_metrics_instance = AccountMetrics.from_json(json)
# print the JSON string representation of the object
print(AccountMetrics.to_json())

# convert the object into a dict
account_metrics_dict = account_metrics_instance.to_dict()
# create an instance of AccountMetrics from a dict
account_metrics_from_dict = AccountMetrics.from_dict(account_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


