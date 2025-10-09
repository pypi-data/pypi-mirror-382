# IneligibleBillingAdjustment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adjustment_id** | **str** | The system generated Adjustment Id.  | [optional] 
**adjustment_number** | **str** | The system generated Adjustment Number.  | [optional] 
**amount** | **decimal.Decimal** | The amount of the adjustment.  | [optional] 
**billing_date** | **date** | The billing date of the adjustment.  | [optional] 
**charge_number** | **str** | The charge number in the subscription for which the adjustment is created. | [optional] 
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**delivery_date** | **date** | The adjustment date, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**delivery_day** | **str** | The adjustment day of the week.  | [optional] 
**eligible** | **bool** | The eligible flag is set as false for an unsuccessful adjustment.  | [optional] 
**error_message** | **str** | The reason due to which an adjustment is not eligible on the given date.  | [optional] 
**reason** | **str** | The reason for the adjustment.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule. | [optional] 
**status** | **str** | The status of the adjustment.  | [optional] 
**subscription_number** | **str** | The subscription number for which the adjustment is created.  | [optional] 

## Example

```python
from zuora_sdk.models.ineligible_billing_adjustment import IneligibleBillingAdjustment

# TODO update the JSON string below
json = "{}"
# create an instance of IneligibleBillingAdjustment from a JSON string
ineligible_billing_adjustment_instance = IneligibleBillingAdjustment.from_json(json)
# print the JSON string representation of the object
print(IneligibleBillingAdjustment.to_json())

# convert the object into a dict
ineligible_billing_adjustment_dict = ineligible_billing_adjustment_instance.to_dict()
# create an instance of IneligibleBillingAdjustment from a dict
ineligible_billing_adjustment_from_dict = IneligibleBillingAdjustment.from_dict(ineligible_billing_adjustment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


