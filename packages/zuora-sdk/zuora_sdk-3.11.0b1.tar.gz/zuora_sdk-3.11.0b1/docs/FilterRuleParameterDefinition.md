# FilterRuleParameterDefinition

Definition of a filter rule parameter. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** |  | [optional] 
**display_name** | **str** | The display name of the parameter.  | [optional] 
**options** | **List[str]** | The option values of the parameter.  | [optional] 
**value_type** | [**FilterRuleParameterDefinitionValueType**](FilterRuleParameterDefinitionValueType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.filter_rule_parameter_definition import FilterRuleParameterDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of FilterRuleParameterDefinition from a JSON string
filter_rule_parameter_definition_instance = FilterRuleParameterDefinition.from_json(json)
# print the JSON string representation of the object
print(FilterRuleParameterDefinition.to_json())

# convert the object into a dict
filter_rule_parameter_definition_dict = filter_rule_parameter_definition_instance.to_dict()
# create an instance of FilterRuleParameterDefinition from a dict
filter_rule_parameter_definition_from_dict = FilterRuleParameterDefinition.from_dict(filter_rule_parameter_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


