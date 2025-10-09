# ExportWorkflowVersionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**linkages** | [**List[Linkage]**](Linkage.md) |  | [optional] 
**tasks** | [**List[Task]**](Task.md) |  | [optional] 
**workflow** | [**Workflow**](Workflow.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.export_workflow_version_response import ExportWorkflowVersionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExportWorkflowVersionResponse from a JSON string
export_workflow_version_response_instance = ExportWorkflowVersionResponse.from_json(json)
# print the JSON string representation of the object
print(ExportWorkflowVersionResponse.to_json())

# convert the object into a dict
export_workflow_version_response_dict = export_workflow_version_response_instance.to_dict()
# create an instance of ExportWorkflowVersionResponse from a dict
export_workflow_version_response_from_dict = ExportWorkflowVersionResponse.from_dict(export_workflow_version_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


