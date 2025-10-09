# CreateDeploymentTemplateRequest

CreateTemplateRequestContent object contains information for creating template. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**SettingSourceComponent**](SettingSourceComponent.md) |  | [optional] 
**custom_fields** | **bool** | Selected custom fields component or not. | [optional] 
**custom_objects** | **bool** | Selected custom objects component or not. | [optional] 
**description** | **str** | Creates template description. | 
**name** | **str** | Name of the Template. | 
**notifications** | **bool** | Selected Notification component or not. | [optional] 
**selected_components** | [**List[ConfigurationTemplateContent]**](ConfigurationTemplateContent.md) | ConfigurationTemplateContent object contains the selected meta data information. | [optional] 
**settings** | **bool** | Selected Settings component or not. | [optional] 
**template_tenant** | **str** | ID of the template tenant. | 
**workflows** | **bool** | Selected Workflow component or not. | [optional] 

## Example

```python
from zuora_sdk.models.create_deployment_template_request import CreateDeploymentTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDeploymentTemplateRequest from a JSON string
create_deployment_template_request_instance = CreateDeploymentTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDeploymentTemplateRequest.to_json())

# convert the object into a dict
create_deployment_template_request_dict = create_deployment_template_request_instance.to_dict()
# create an instance of CreateDeploymentTemplateRequest from a dict
create_deployment_template_request_from_dict = CreateDeploymentTemplateRequest.from_dict(create_deployment_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


