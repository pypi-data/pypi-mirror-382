# RevproAccountingCodes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adjustment_liability_account** | **str** | The name of the account where the Account Type is \&quot;Adjustment Liability\&quot;. | 
**adjustment_revenue_account** | **str** | The name of the account where the Account Type is \&quot;Adjustment Revenue\&quot;. | 
**contract_asset_account** | **str** | The name of the account where the Account Type is \&quot;Contract Asset\&quot;. | 
**contract_liability_account** | **str** | The name of the account where the Account Type is \&quot;Contract Liability\&quot;. | 
**product_rate_plan_charge_id** | **str** | The ID of your product rate plan charge. | 
**recognized_revenue_account** | **str** | The name of the account where the Account Type is \&quot;Recognized Revenue\&quot;. | 
**unbilled_receivables_account** | **str** | The name of the account where the Account Type is \&quot;Unbilled Receivables\&quot;. | 

## Example

```python
from zuora_sdk.models.revpro_accounting_codes import RevproAccountingCodes

# TODO update the JSON string below
json = "{}"
# create an instance of RevproAccountingCodes from a JSON string
revpro_accounting_codes_instance = RevproAccountingCodes.from_json(json)
# print the JSON string representation of the object
print(RevproAccountingCodes.to_json())

# convert the object into a dict
revpro_accounting_codes_dict = revpro_accounting_codes_instance.to_dict()
# create an instance of RevproAccountingCodes from a dict
revpro_accounting_codes_from_dict = RevproAccountingCodes.from_dict(revpro_accounting_codes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


