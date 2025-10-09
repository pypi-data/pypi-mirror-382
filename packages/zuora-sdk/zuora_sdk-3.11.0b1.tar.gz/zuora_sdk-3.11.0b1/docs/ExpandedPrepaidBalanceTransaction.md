# ExpandedPrepaidBalanceTransaction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**prepaid_balance_id** | **str** |  | [optional] 
**fund_id** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**balance** | **float** |  | [optional] 
**source_id** | **str** |  | [optional] 
**transaction_date** | **date** |  | [optional] 
**transaction_source_type** | **str** |  | [optional] 
**prepaid_balance_transaction_type** | **str** |  | [optional] 
**usage_uom** | **str** |  | [optional] 
**drawdown_rate** | **float** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**prepaid_balance** | [**ExpandedPrepaidBalance**](ExpandedPrepaidBalance.md) |  | [optional] 
**fund** | [**ExpandedPrepaidBalanceFund**](ExpandedPrepaidBalanceFund.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_prepaid_balance_transaction import ExpandedPrepaidBalanceTransaction

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPrepaidBalanceTransaction from a JSON string
expanded_prepaid_balance_transaction_instance = ExpandedPrepaidBalanceTransaction.from_json(json)
# print the JSON string representation of the object
print(ExpandedPrepaidBalanceTransaction.to_json())

# convert the object into a dict
expanded_prepaid_balance_transaction_dict = expanded_prepaid_balance_transaction_instance.to_dict()
# create an instance of ExpandedPrepaidBalanceTransaction from a dict
expanded_prepaid_balance_transaction_from_dict = ExpandedPrepaidBalanceTransaction.from_dict(expanded_prepaid_balance_transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


