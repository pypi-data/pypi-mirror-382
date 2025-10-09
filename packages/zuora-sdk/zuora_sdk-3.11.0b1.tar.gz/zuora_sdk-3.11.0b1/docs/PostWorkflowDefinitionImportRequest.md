# PostWorkflowDefinitionImportRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**linkages** | [**List[Linkage]**](Linkage.md) |  | [optional] 
**tasks** | [**List[Task]**](Task.md) |  | [optional] 
**workflow** | [**Workflow**](Workflow.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.post_workflow_definition_import_request import PostWorkflowDefinitionImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkflowDefinitionImportRequest from a JSON string
post_workflow_definition_import_request_instance = PostWorkflowDefinitionImportRequest.from_json(json)
# print the JSON string representation of the object
print(PostWorkflowDefinitionImportRequest.to_json())

# convert the object into a dict
post_workflow_definition_import_request_dict = post_workflow_definition_import_request_instance.to_dict()
# create an instance of PostWorkflowDefinitionImportRequest from a dict
post_workflow_definition_import_request_from_dict = PostWorkflowDefinitionImportRequest.from_dict(post_workflow_definition_import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


