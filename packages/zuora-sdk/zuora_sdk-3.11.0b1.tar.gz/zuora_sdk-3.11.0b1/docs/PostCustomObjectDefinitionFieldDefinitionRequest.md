# PostCustomObjectDefinitionFieldDefinitionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **bool** | Indicates whether to use this field as the display name of the custom object when being linked to another custom object.   This field applies only to the Text custom field type:   - The &#x60;type&#x60; field is &#x60;string&#x60;.  - The &#x60;enum&#x60; field is not specified. | [optional] 
**format** | **str** | The data format of the custom field | [optional] 
**label** | **str** | The UI label of the custom field | 
**max_length** | **int** | The maximum length of string that can be stored in the custom field.   This field applies only to the following custom field types:   - Text:   - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;format&#x60; field is not specified or is &#x60;url&#x60;.   - The &#x60;enum&#x60; field is not specified. - Picklist:   - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;enum&#x60; field is specified.   - The &#x60;multiselect&#x60; field is not specified or is &#x60;false&#x60;. - Multiselect:   - The &#x60;type&#x60; field is &#x60;string&#x60;.   - The &#x60;enum&#x60; field is specified.   - The &#x60;multiselect&#x60; field is &#x60;true&#x60;.  If the custom field is filterable, the value of &#x60;maxLength&#x60; must be 512 or less. | [optional] 
**multiselect** | **bool** | Indicates whether this is a multiselect custom field.  This field applies only to the Picklist or Multiselect custom field types:  - The &#x60;type&#x60; field is &#x60;string&#x60;. - The &#x60;maxLength&#x60; field is specified. - The &#x60;enum&#x60; field is specified.  | [optional] 
**type** | **str** | The data type of the custom field | 

## Example

```python
from zuora_sdk.models.post_custom_object_definition_field_definition_request import PostCustomObjectDefinitionFieldDefinitionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomObjectDefinitionFieldDefinitionRequest from a JSON string
post_custom_object_definition_field_definition_request_instance = PostCustomObjectDefinitionFieldDefinitionRequest.from_json(json)
# print the JSON string representation of the object
print(PostCustomObjectDefinitionFieldDefinitionRequest.to_json())

# convert the object into a dict
post_custom_object_definition_field_definition_request_dict = post_custom_object_definition_field_definition_request_instance.to_dict()
# create an instance of PostCustomObjectDefinitionFieldDefinitionRequest from a dict
post_custom_object_definition_field_definition_request_from_dict = PostCustomObjectDefinitionFieldDefinitionRequest.from_dict(post_custom_object_definition_field_definition_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


