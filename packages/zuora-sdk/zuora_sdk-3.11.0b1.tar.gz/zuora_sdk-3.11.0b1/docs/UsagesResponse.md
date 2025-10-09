# UsagesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metrics** | [**List[Usage]**](Usage.md) | The list of tasks retrieved.  | [optional] 

## Example

```python
from zuora_sdk.models.usages_response import UsagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UsagesResponse from a JSON string
usages_response_instance = UsagesResponse.from_json(json)
# print the JSON string representation of the object
print(UsagesResponse.to_json())

# convert the object into a dict
usages_response_dict = usages_response_instance.to_dict()
# create an instance of UsagesResponse from a dict
usages_response_from_dict = UsagesResponse.from_dict(usages_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


