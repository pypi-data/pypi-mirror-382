# WorkflowError


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | [**WorkflowErrorCode**](WorkflowErrorCode.md) |  | [optional] 
**status** | **int** | The http status code for this error | [optional] 
**title** | **str** | A human readable description describing the error | [optional] 

## Example

```python
from zuora_sdk.models.workflow_error import WorkflowError

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowError from a JSON string
workflow_error_instance = WorkflowError.from_json(json)
# print the JSON string representation of the object
print(WorkflowError.to_json())

# convert the object into a dict
workflow_error_dict = workflow_error_instance.to_dict()
# create an instance of WorkflowError from a dict
workflow_error_from_dict = WorkflowError.from_dict(workflow_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


