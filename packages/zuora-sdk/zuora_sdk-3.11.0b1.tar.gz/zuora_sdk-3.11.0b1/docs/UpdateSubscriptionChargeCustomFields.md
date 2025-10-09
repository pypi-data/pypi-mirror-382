# UpdateSubscriptionChargeCustomFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 

## Example

```python
from zuora_sdk.models.update_subscription_charge_custom_fields import UpdateSubscriptionChargeCustomFields

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSubscriptionChargeCustomFields from a JSON string
update_subscription_charge_custom_fields_instance = UpdateSubscriptionChargeCustomFields.from_json(json)
# print the JSON string representation of the object
print(UpdateSubscriptionChargeCustomFields.to_json())

# convert the object into a dict
update_subscription_charge_custom_fields_dict = update_subscription_charge_custom_fields_instance.to_dict()
# create an instance of UpdateSubscriptionChargeCustomFields from a dict
update_subscription_charge_custom_fields_from_dict = UpdateSubscriptionChargeCustomFields.from_dict(update_subscription_charge_custom_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


