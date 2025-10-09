# MappingResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mapping** | **object** |  | [optional] 
**dateformat** | **str** |  | [optional] [default to 'DD-MM-YYYY']

## Example

```python
from zuora_sdk.models.mapping_response import MappingResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MappingResponse from a JSON string
mapping_response_instance = MappingResponse.from_json(json)
# print the JSON string representation of the object
print(MappingResponse.to_json())

# convert the object into a dict
mapping_response_dict = mapping_response_instance.to_dict()
# create an instance of MappingResponse from a dict
mapping_response_from_dict = MappingResponse.from_dict(mapping_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


