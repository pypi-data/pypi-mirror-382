# Condition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conditions** | [**List[Condition]**](Condition.md) | The conditions will be combined by the relation.  | [optional] 
**var_field** | **str** | The field name of a single condition.  | [optional] 
**operator** | **str** | The operator of a single condition.  - eq: equal, field &#x3D; value - neq: not equal, field !&#x3D; value - gt: greater than, field &gt; value - lt: less than, field &lt; value - gte: greater than or equal, field &gt;&#x3D; value - lte: less than or equal, field &lt;&#x3D; value - lk: like, field like value - in: in, field in value, multiple values are separated by comma - nl: null, field is null - nnl: not null, field is not null | [optional] 
**relation** | **str** | The relation among the conditions.  | [optional] 
**value** | **str** | The value of a single condition.  | [optional] 

## Example

```python
from zuora_sdk.models.condition import Condition

# TODO update the JSON string below
json = "{}"
# create an instance of Condition from a JSON string
condition_instance = Condition.from_json(json)
# print the JSON string representation of the object
print(Condition.to_json())

# convert the object into a dict
condition_dict = condition_instance.to_dict()
# create an instance of Condition from a dict
condition_from_dict = Condition.from_dict(condition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


