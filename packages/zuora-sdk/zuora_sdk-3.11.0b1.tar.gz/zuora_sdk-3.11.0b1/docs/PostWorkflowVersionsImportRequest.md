# PostWorkflowVersionsImportRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow** | [**DetailedWorkflow**](DetailedWorkflow.md) |  | [optional] 
**tasks** | [**List[Task]**](Task.md) |  | [optional] 
**linkages** | [**List[Linkage]**](Linkage.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.post_workflow_versions_import_request import PostWorkflowVersionsImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostWorkflowVersionsImportRequest from a JSON string
post_workflow_versions_import_request_instance = PostWorkflowVersionsImportRequest.from_json(json)
# print the JSON string representation of the object
print(PostWorkflowVersionsImportRequest.to_json())

# convert the object into a dict
post_workflow_versions_import_request_dict = post_workflow_versions_import_request_instance.to_dict()
# create an instance of PostWorkflowVersionsImportRequest from a dict
post_workflow_versions_import_request_from_dict = PostWorkflowVersionsImportRequest.from_dict(post_workflow_versions_import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


