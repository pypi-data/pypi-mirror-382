# ProductRatePlanChargeFinanceInformation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts_receivable_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Accounts Receivable\&quot;. | [optional] 
**deferred_revenue_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Deferred Revenue\&quot;. | [optional] 
**recognized_revenue_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Recognized Revenue\&quot;. | [optional] 
**adjustment_liability_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Adjustment Liability\&quot;. | [optional] 
**adjustment_revenue_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Adjustment Revenue\&quot;. | [optional] 
**contract_asset_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Contract Asset\&quot;. | [optional] 
**contract_liability_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Contract Liability\&quot;. | [optional] 
**unbilled_receivables_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Unbilled Receivables\&quot;. | [optional] 
**contract_recognized_revenue_accounting_code** | **str** | The name of the account where the Account Type is \&quot;Recognized Revenue\&quot;. | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_charge_finance_information import ProductRatePlanChargeFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanChargeFinanceInformation from a JSON string
product_rate_plan_charge_finance_information_instance = ProductRatePlanChargeFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanChargeFinanceInformation.to_json())

# convert the object into a dict
product_rate_plan_charge_finance_information_dict = product_rate_plan_charge_finance_information_instance.to_dict()
# create an instance of ProductRatePlanChargeFinanceInformation from a dict
product_rate_plan_charge_finance_information_from_dict = ProductRatePlanChargeFinanceInformation.from_dict(product_rate_plan_charge_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


