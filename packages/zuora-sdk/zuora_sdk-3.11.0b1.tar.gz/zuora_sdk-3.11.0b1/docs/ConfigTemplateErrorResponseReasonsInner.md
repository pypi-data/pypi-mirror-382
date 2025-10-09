# ConfigTemplateErrorResponseReasonsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code of response.  | [optional] 
**message** | **str** | A detailed description of the error response. | [optional] 

## Example

```python
from zuora_sdk.models.config_template_error_response_reasons_inner import ConfigTemplateErrorResponseReasonsInner

# TODO update the JSON string below
json = "{}"
# create an instance of ConfigTemplateErrorResponseReasonsInner from a JSON string
config_template_error_response_reasons_inner_instance = ConfigTemplateErrorResponseReasonsInner.from_json(json)
# print the JSON string representation of the object
print(ConfigTemplateErrorResponseReasonsInner.to_json())

# convert the object into a dict
config_template_error_response_reasons_inner_dict = config_template_error_response_reasons_inner_instance.to_dict()
# create an instance of ConfigTemplateErrorResponseReasonsInner from a dict
config_template_error_response_reasons_inner_from_dict = ConfigTemplateErrorResponseReasonsInner.from_dict(config_template_error_response_reasons_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


