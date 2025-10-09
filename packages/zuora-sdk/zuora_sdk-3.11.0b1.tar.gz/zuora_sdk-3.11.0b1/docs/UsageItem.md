# UsageItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique ID for the usage item.  | [optional] 
**account_id** | **str** | Customer account ID.  | [optional] 
**account_name** | **str** | Customer account name.  | [optional] 
**account_number** | **str** | Customer account number.  | [optional] 
**product_rate_plan_charge_number** | **str** | Product rate plan charge number. **Note**: This field is only available if you have the [Dynamic Usage Charge] enabled.  | [optional] 
**subscription_number** | **str** | Number of the subscription covering this usage.  | [optional] 
**charge_number** | **str** | Number of the rate-plan charge that pays for this usage.  | [optional] 
**start_date_time** | **str** | Start date of the time period in which usage is tracked. Zuora uses this field value to determine the usage date. | [optional] 
**unit_of_measure** | **str** | Unit used to measure consumption.  | [optional] 
**quantity** | **decimal.Decimal** | Number of units used.  | [optional] 
**source_name** | **str** | Source of the usage data. Possible values are: &#x60;Import&#x60;, &#x60;API&#x60;.  | [optional] 
**file_name** | **str** | The name of the import file when the usage record is imported from the file. | [optional] 
**status** | **str** | Possible values are: &#x60;Importing&#x60;, &#x60;Pending&#x60;, &#x60;Processed&#x60;.  | [optional] 
**submission_date_time** | **str** | Date when usage was submitted.  | [optional] 
**unique_key** | **str** | a customer-defined specific identifier of a usage record.   **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) or  [Unbilled Usage](https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_for_usage_or_prepaid_products/Advanced_Consumption_Billing/Unbilled_Usage) feature enabled. See [Upload usage record with unique key](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Prepaid_balance_transactions#Upload_usage_record_with_unique_key) for more information. | [optional] 

## Example

```python
from zuora_sdk.models.usage_item import UsageItem

# TODO update the JSON string below
json = "{}"
# create an instance of UsageItem from a JSON string
usage_item_instance = UsageItem.from_json(json)
# print the JSON string representation of the object
print(UsageItem.to_json())

# convert the object into a dict
usage_item_dict = usage_item_instance.to_dict()
# create an instance of UsageItem from a dict
usage_item_from_dict = UsageItem.from_dict(usage_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


