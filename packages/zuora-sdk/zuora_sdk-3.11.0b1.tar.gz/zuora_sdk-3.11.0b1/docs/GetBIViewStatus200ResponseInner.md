# GetBIViewStatus200ResponseInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**task_id** | **str** | The unique identifier for the task. | [optional] 
**status** | **str** | The current status of the task (e.g., RUNNING, COMPLETED). | [optional] 
**message** | **str** | Additional information about the task. | [optional] 

## Example

```python
from zuora_sdk.models.get_bi_view_status200_response_inner import GetBIViewStatus200ResponseInner

# TODO update the JSON string below
json = "{}"
# create an instance of GetBIViewStatus200ResponseInner from a JSON string
get_bi_view_status200_response_inner_instance = GetBIViewStatus200ResponseInner.from_json(json)
# print the JSON string representation of the object
print(GetBIViewStatus200ResponseInner.to_json())

# convert the object into a dict
get_bi_view_status200_response_inner_dict = get_bi_view_status200_response_inner_instance.to_dict()
# create an instance of GetBIViewStatus200ResponseInner from a dict
get_bi_view_status200_response_inner_from_dict = GetBIViewStatus200ResponseInner.from_dict(get_bi_view_status200_response_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


