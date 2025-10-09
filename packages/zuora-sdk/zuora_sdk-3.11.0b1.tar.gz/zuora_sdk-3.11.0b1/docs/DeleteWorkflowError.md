# DeleteWorkflowError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | **List[str]** | The error messages | [optional] 

## Example

```python
from zuora_sdk.models.delete_workflow_error import DeleteWorkflowError

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteWorkflowError from a JSON string
delete_workflow_error_instance = DeleteWorkflowError.from_json(json)
# print the JSON string representation of the object
print(DeleteWorkflowError.to_json())

# convert the object into a dict
delete_workflow_error_dict = delete_workflow_error_instance.to_dict()
# create an instance of DeleteWorkflowError from a dict
delete_workflow_error_from_dict = DeleteWorkflowError.from_dict(delete_workflow_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


