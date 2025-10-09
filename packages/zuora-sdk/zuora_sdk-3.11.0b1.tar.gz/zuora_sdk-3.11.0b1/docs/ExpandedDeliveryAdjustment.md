# ExpandedDeliveryAdjustment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**adjustment_number** | **str** |  | [optional] 
**credit_memo_number** | **str** |  | [optional] 
**debit_memo_number** | **str** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**segment_id** | **str** |  | [optional] 
**charge_id** | **str** |  | [optional] 
**charge_number** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**original_sub_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**amount_per_unit** | **float** |  | [optional] 
**amount** | **float** |  | [optional] 
**var_date** | **date** |  | [optional] 
**delivery_day** | **str** |  | [optional] 
**reason** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**invoice_owner_account_id** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**deferred_accounting_code** | **str** |  | [optional] 
**recognized_revenue_accounting_code** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**billing_date** | **date** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_delivery_adjustment import ExpandedDeliveryAdjustment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedDeliveryAdjustment from a JSON string
expanded_delivery_adjustment_instance = ExpandedDeliveryAdjustment.from_json(json)
# print the JSON string representation of the object
print(ExpandedDeliveryAdjustment.to_json())

# convert the object into a dict
expanded_delivery_adjustment_dict = expanded_delivery_adjustment_instance.to_dict()
# create an instance of ExpandedDeliveryAdjustment from a dict
expanded_delivery_adjustment_from_dict = ExpandedDeliveryAdjustment.from_dict(expanded_delivery_adjustment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


