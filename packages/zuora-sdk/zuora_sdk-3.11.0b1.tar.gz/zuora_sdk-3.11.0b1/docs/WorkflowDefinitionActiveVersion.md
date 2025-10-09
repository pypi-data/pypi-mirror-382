# WorkflowDefinitionActiveVersion

Information of the active version.  

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the active version.  | [optional] 
**id** | **int** | The unique ID of the active version.  | [optional] 
**status** | **str** | The status of the active version.  | [optional] 
**type** | [**WorkflowDefinitionActiveVersionType**](WorkflowDefinitionActiveVersionType.md) |  | [optional] 
**version** | **str** | The version number of the active version.  | [optional] 

## Example

```python
from zuora_sdk.models.workflow_definition_active_version import WorkflowDefinitionActiveVersion

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionActiveVersion from a JSON string
workflow_definition_active_version_instance = WorkflowDefinitionActiveVersion.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionActiveVersion.to_json())

# convert the object into a dict
workflow_definition_active_version_dict = workflow_definition_active_version_instance.to_dict()
# create an instance of WorkflowDefinitionActiveVersion from a dict
workflow_definition_active_version_from_dict = WorkflowDefinitionActiveVersion.from_dict(workflow_definition_active_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


