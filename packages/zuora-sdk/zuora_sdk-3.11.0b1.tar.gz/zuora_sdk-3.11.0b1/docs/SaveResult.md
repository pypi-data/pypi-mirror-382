# SaveResult


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[ActionsErrorResponse]**](ActionsErrorResponse.md) |  | [optional] 
**id** | **str** |  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.save_result import SaveResult

# TODO update the JSON string below
json = "{}"
# create an instance of SaveResult from a JSON string
save_result_instance = SaveResult.from_json(json)
# print the JSON string representation of the object
print(SaveResult.to_json())

# convert the object into a dict
save_result_dict = save_result_instance.to_dict()
# create an instance of SaveResult from a dict
save_result_from_dict = SaveResult.from_dict(save_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


