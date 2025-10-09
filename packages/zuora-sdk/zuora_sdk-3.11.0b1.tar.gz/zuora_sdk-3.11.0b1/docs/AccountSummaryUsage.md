# AccountSummaryUsage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**quantity** | **decimal.Decimal** | Number of units used.  | [optional] 
**start_date** | **str** | The start date of a usage period as &#x60;yyyy-mm&#x60;. Zuora uses this field value to determine the usage date. | [optional] 
**unit_of_measure** | **str** | Unit by which consumption is measured, as configured in the Billing Settings section of the web-based UI. | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_usage import AccountSummaryUsage

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryUsage from a JSON string
account_summary_usage_instance = AccountSummaryUsage.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryUsage.to_json())

# convert the object into a dict
account_summary_usage_dict = account_summary_usage_instance.to_dict()
# create an instance of AccountSummaryUsage from a dict
account_summary_usage_from_dict = AccountSummaryUsage.from_dict(account_summary_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


