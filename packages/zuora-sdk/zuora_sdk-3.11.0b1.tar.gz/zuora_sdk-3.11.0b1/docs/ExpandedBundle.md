# ExpandedBundle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**bundle_id** | **str** |  | [optional] 
**component_id** | **str** |  | [optional] 
**component_type** | **str** |  | [optional] 
**bundle_config** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_bundle import ExpandedBundle

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedBundle from a JSON string
expanded_bundle_instance = ExpandedBundle.from_json(json)
# print the JSON string representation of the object
print(ExpandedBundle.to_json())

# convert the object into a dict
expanded_bundle_dict = expanded_bundle_instance.to_dict()
# create an instance of ExpandedBundle from a dict
expanded_bundle_from_dict = ExpandedBundle.from_dict(expanded_bundle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


