# Linkage

Used to represent the relationship between workflow tasks

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**linkage_type** | [**LinkageLinkageType**](LinkageLinkageType.md) |  | [optional] 
**source_task_id** | **int** | the task that spawned the target task | [optional] 
**source_workflow_id** | **int** | the workflow the target task is associated with | [optional] 
**target_task_id** | **int** | the task that the source task is linked to. | [optional] 

## Example

```python
from zuora_sdk.models.linkage import Linkage

# TODO update the JSON string below
json = "{}"
# create an instance of Linkage from a JSON string
linkage_instance = Linkage.from_json(json)
# print the JSON string representation of the object
print(Linkage.to_json())

# convert the object into a dict
linkage_dict = linkage_instance.to_dict()
# create an instance of Linkage from a dict
linkage_from_dict = Linkage.from_dict(linkage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


