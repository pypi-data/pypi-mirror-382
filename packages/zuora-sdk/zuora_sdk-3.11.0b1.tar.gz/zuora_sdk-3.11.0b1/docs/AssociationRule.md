# AssociationRule

 Customers can define Commitment associations with Subscription Charges using filter. in phase#1, we only supports explicitly associate the commitment with a list of charge numbers. { \"objectType\": \"RatePlanCharge\", \"condition\": { \"relation\": \"and\", \"conditions\": [ { \"field\": \"chargeNumber\", \"operator\": \"in\", \"value\": \"C-0001,c-0002\" } ] } } 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition** | [**Condition**](Condition.md) |  | [optional] 
**object_type** | **str** | The target object type of the condition.  | [optional] 

## Example

```python
from zuora_sdk.models.association_rule import AssociationRule

# TODO update the JSON string below
json = "{}"
# create an instance of AssociationRule from a JSON string
association_rule_instance = AssociationRule.from_json(json)
# print the JSON string representation of the object
print(AssociationRule.to_json())

# convert the object into a dict
association_rule_dict = association_rule_instance.to_dict()
# create an instance of AssociationRule from a dict
association_rule_from_dict = AssociationRule.from_dict(association_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


