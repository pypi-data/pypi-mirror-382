# CustomObjectCustomFieldDefinition

The custom field definition in the custom object

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **bool** | Indicates whether to use this field as the display name of the custom object when being linked to another custom object.  This field applies only to the Text custom field type:  - The &#x60;type&#x60; field is &#x60;string&#x60;. - The &#x60;enum&#x60; field is not specified.  | [optional] 
**format** | **str** | The data format of the custom field | [optional] 
**label** | **str** | The UI label of the custom field | [optional] 
**max_length** | **int** | The maximum length of string that can be stored in the custom field.  nThis field applies only to the following custom field types:  - Text:  - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;format&#x60; field is not specified or is &#x60;url&#x60;.   - The &#x60;enum&#x60; field is not specified. - Picklist:   - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;enum&#x60; field is specified.   - The &#x60;multiselect&#x60; field is not specified or is &#x60;false&#x60;. - Multiselect:   - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;enum&#x60; field is specified.   - The &#x60;multiselect&#x60; field is &#x60;true&#x60;.  | [optional] 
**multiselect** | **bool** | Indicates whether this is a multiselect custom field.  This field applies only to the Picklist or Multiselect custom field types:  - The &#x60;type&#x60; field is &#x60;string&#x60;. - The &#x60;maxLength&#x60; field is specified. - The &#x60;enum&#x60; field is specified.  | [optional] 
**origin** | [**CustomObjectCustomFieldDefinitionOrigin**](CustomObjectCustomFieldDefinitionOrigin.md) |  | [optional] 
**type** | **str** | The data type of the custom field | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_custom_field_definition import CustomObjectCustomFieldDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectCustomFieldDefinition from a JSON string
custom_object_custom_field_definition_instance = CustomObjectCustomFieldDefinition.from_json(json)
# print the JSON string representation of the object
print(CustomObjectCustomFieldDefinition.to_json())

# convert the object into a dict
custom_object_custom_field_definition_dict = custom_object_custom_field_definition_instance.to_dict()
# create an instance of CustomObjectCustomFieldDefinition from a dict
custom_object_custom_field_definition_from_dict = CustomObjectCustomFieldDefinition.from_dict(custom_object_custom_field_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


