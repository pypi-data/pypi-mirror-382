# PostRunWorkflow400Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[WorkflowError]**](WorkflowError.md) | The list of errors returned from the workflow | [optional] 

## Example

```python
from zuora_sdk.models.post_run_workflow400_response import PostRunWorkflow400Response

# TODO update the JSON string below
json = "{}"
# create an instance of PostRunWorkflow400Response from a JSON string
post_run_workflow400_response_instance = PostRunWorkflow400Response.from_json(json)
# print the JSON string representation of the object
print(PostRunWorkflow400Response.to_json())

# convert the object into a dict
post_run_workflow400_response_dict = post_run_workflow400_response_instance.to_dict()
# create an instance of PostRunWorkflow400Response from a dict
post_run_workflow400_response_from_dict = PostRunWorkflow400Response.from_dict(post_run_workflow400_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


