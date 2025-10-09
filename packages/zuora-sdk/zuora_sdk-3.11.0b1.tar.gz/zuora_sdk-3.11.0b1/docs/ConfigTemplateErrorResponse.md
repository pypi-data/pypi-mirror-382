# ConfigTemplateErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reasons** | [**List[ConfigTemplateErrorResponseReasonsInner]**](ConfigTemplateErrorResponseReasonsInner.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.config_template_error_response import ConfigTemplateErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConfigTemplateErrorResponse from a JSON string
config_template_error_response_instance = ConfigTemplateErrorResponse.from_json(json)
# print the JSON string representation of the object
print(ConfigTemplateErrorResponse.to_json())

# convert the object into a dict
config_template_error_response_dict = config_template_error_response_instance.to_dict()
# create an instance of ConfigTemplateErrorResponse from a dict
config_template_error_response_from_dict = ConfigTemplateErrorResponse.from_dict(config_template_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


