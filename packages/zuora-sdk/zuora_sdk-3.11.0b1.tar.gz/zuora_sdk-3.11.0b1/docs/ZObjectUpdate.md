# ZObjectUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**fields_to_null** | **List[str]** | Used to set a list of fields to null.  | [optional] 

## Example

```python
from zuora_sdk.models.z_object_update import ZObjectUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ZObjectUpdate from a JSON string
z_object_update_instance = ZObjectUpdate.from_json(json)
# print the JSON string representation of the object
print(ZObjectUpdate.to_json())

# convert the object into a dict
z_object_update_dict = z_object_update_instance.to_dict()
# create an instance of ZObjectUpdate from a dict
z_object_update_from_dict = ZObjectUpdate.from_dict(z_object_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


