# BillingAdjustment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**adjustment_id** | **str** | The system generated Adjustment Id.  | [optional] 
**adjustment_number** | **str** | The system generated Adjustment Number.  | [optional] 
**amount** | **decimal.Decimal** | The amount of the adjustment.  | [optional] 
**billing_date** | **date** | The billing date is same as the delivery date of the adjustment, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**charge_number** | **str** | The charge number in the subscription for which the adjustment is created. | [optional] 
**credit_memo_number** | **str** | The Credit Memo generated for the adjustment.  | [optional] 
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**delivery_date** | **date** | The adjustment date, in &#x60;yyyy-mm-dd&#x60; format.  | [optional] 
**delivery_day** | **str** | The adjustment day of the week.  | [optional] 
**eligible** | **bool** | The eligible flag is set as true for a successfully created adjustment. | [optional] 
**reason** | **str** | The reason for the adjustment.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule. | [optional] 
**status** | **str** | The status of the adjustment will be &#x60;Billed&#x60; or &#x60;Cancelled&#x60;.  | [optional] 
**subscription_number** | **str** | The subscription number for which the adjustment is created.  | [optional] 

## Example

```python
from zuora_sdk.models.billing_adjustment import BillingAdjustment

# TODO update the JSON string below
json = "{}"
# create an instance of BillingAdjustment from a JSON string
billing_adjustment_instance = BillingAdjustment.from_json(json)
# print the JSON string representation of the object
print(BillingAdjustment.to_json())

# convert the object into a dict
billing_adjustment_dict = billing_adjustment_instance.to_dict()
# create an instance of BillingAdjustment from a dict
billing_adjustment_from_dict = BillingAdjustment.from_dict(billing_adjustment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


