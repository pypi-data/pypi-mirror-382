# DeploymentTemplate

Contains all template details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | Whether or not the template is active. | [optional] 
**content** | [**SettingSourceComponent**](SettingSourceComponent.md) |  | [optional] 
**created_by** | **str** | Information about the user who created it. | [optional] 
**created_on** | **str** | When it is created. | [optional] 
**description** | **str** | Template description which contains the information about the created template. | [optional] 
**entity_name** | **str** | Name of the Entity | [optional] 
**environment** | **str** | Details of the environment in which the template was created. | [optional] 
**errors** | **str** | Error information. | [optional] 
**id** | **str** | Id of the template. | [optional] 
**name** | **str** | Name of the template. | [optional] 
**status** | **str** | The status of the template creation, such as whether it is in progress, completed, or failed. | [optional] 
**tenant_name** | **str** | Tenant&#39;s name for whom the template is created. | [optional] 

## Example

```python
from zuora_sdk.models.deployment_template import DeploymentTemplate

# TODO update the JSON string below
json = "{}"
# create an instance of DeploymentTemplate from a JSON string
deployment_template_instance = DeploymentTemplate.from_json(json)
# print the JSON string representation of the object
print(DeploymentTemplate.to_json())

# convert the object into a dict
deployment_template_dict = deployment_template_instance.to_dict()
# create an instance of DeploymentTemplate from a dict
deployment_template_from_dict = DeploymentTemplate.from_dict(deployment_template_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


