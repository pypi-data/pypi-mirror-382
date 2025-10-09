# CompareSchemaKeyValue

When a comparison is made between a source and target tenant, it sends a response to the user interface.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**difference** | **Dict[str, List[str]]** | Returns the different components list. | [optional] 
**response** | [**List[MigrationComponentContent]**](MigrationComponentContent.md) | Provides the total reponse of the components. | [optional] 
**segregation_keys** | **List[str]** | Provides separation of components. | [optional] 

## Example

```python
from zuora_sdk.models.compare_schema_key_value import CompareSchemaKeyValue

# TODO update the JSON string below
json = "{}"
# create an instance of CompareSchemaKeyValue from a JSON string
compare_schema_key_value_instance = CompareSchemaKeyValue.from_json(json)
# print the JSON string representation of the object
print(CompareSchemaKeyValue.to_json())

# convert the object into a dict
compare_schema_key_value_dict = compare_schema_key_value_instance.to_dict()
# create an instance of CompareSchemaKeyValue from a dict
compare_schema_key_value_from_dict = CompareSchemaKeyValue.from_dict(compare_schema_key_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


