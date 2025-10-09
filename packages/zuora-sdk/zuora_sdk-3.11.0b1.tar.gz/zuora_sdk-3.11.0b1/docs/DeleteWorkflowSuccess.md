# DeleteWorkflowSuccess


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The id of the deleted workflow | [optional] 
**success** | **bool** | The indicator for whether the deletion was a success | [optional] 

## Example

```python
from zuora_sdk.models.delete_workflow_success import DeleteWorkflowSuccess

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteWorkflowSuccess from a JSON string
delete_workflow_success_instance = DeleteWorkflowSuccess.from_json(json)
# print the JSON string representation of the object
print(DeleteWorkflowSuccess.to_json())

# convert the object into a dict
delete_workflow_success_dict = delete_workflow_success_instance.to_dict()
# create an instance of DeleteWorkflowSuccess from a dict
delete_workflow_success_from_dict = DeleteWorkflowSuccess.from_dict(delete_workflow_success_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


