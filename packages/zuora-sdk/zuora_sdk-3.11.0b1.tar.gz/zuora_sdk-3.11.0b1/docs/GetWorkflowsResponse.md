# GetWorkflowsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[WorkflowDefinitionAndVersions]**](WorkflowDefinitionAndVersions.md) | The list of workflows retrieved.   | [optional] 
**pagination** | [**GetWorkflowsResponsePagination**](GetWorkflowsResponsePagination.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_workflows_response import GetWorkflowsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetWorkflowsResponse from a JSON string
get_workflows_response_instance = GetWorkflowsResponse.from_json(json)
# print the JSON string representation of the object
print(GetWorkflowsResponse.to_json())

# convert the object into a dict
get_workflows_response_dict = get_workflows_response_instance.to_dict()
# create an instance of GetWorkflowsResponse from a dict
get_workflows_response_from_dict = GetWorkflowsResponse.from_dict(get_workflows_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


