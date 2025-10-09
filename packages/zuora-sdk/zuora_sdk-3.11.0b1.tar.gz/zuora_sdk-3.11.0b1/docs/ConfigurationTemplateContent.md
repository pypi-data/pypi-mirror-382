# ConfigurationTemplateContent

It contains information about template schemas with segregation keys.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**component_type** | **str** | Type of Component. | [optional] 
**error** | **str** | Error Information. | [optional] 
**id** | **str** | Id of Each component. | [optional] 
**key** | **str** | Key value of fields inside component. | [optional] 
**method** | **str** | Http method which is used to retrieve the particular component. | [optional] 
**payload** | **object** | Json node object contains metadata. | [optional] 
**result** | **str** | Contains the response of details fetched regarding selected component. | [optional] 
**segregation_key** | **str** | Gives the difference between components and sub components. | [optional] 
**template_id** | **str** | Id of the Template. | [optional] 
**url** | **str** | Metadata is retrieved from this URL. | [optional] 

## Example

```python
from zuora_sdk.models.configuration_template_content import ConfigurationTemplateContent

# TODO update the JSON string below
json = "{}"
# create an instance of ConfigurationTemplateContent from a JSON string
configuration_template_content_instance = ConfigurationTemplateContent.from_json(json)
# print the JSON string representation of the object
print(ConfigurationTemplateContent.to_json())

# convert the object into a dict
configuration_template_content_dict = configuration_template_content_instance.to_dict()
# create an instance of ConfigurationTemplateContent from a dict
configuration_template_content_from_dict = ConfigurationTemplateContent.from_dict(configuration_template_content_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


