# DeploymentTemplatesResponse

It contains a collection of all the templates that have been created.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**List[DeploymentTemplate]**](DeploymentTemplate.md) | Contains list of template details. | [optional] 

## Example

```python
from zuora_sdk.models.deployment_templates_response import DeploymentTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeploymentTemplatesResponse from a JSON string
deployment_templates_response_instance = DeploymentTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(DeploymentTemplatesResponse.to_json())

# convert the object into a dict
deployment_templates_response_dict = deployment_templates_response_instance.to_dict()
# create an instance of DeploymentTemplatesResponse from a dict
deployment_templates_response_from_dict = DeploymentTemplatesResponse.from_dict(deployment_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


