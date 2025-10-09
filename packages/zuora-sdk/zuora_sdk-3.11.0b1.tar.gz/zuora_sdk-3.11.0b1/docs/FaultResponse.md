# FaultResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fault_code** | **str** | The fault code.  | [optional] 
**fault_message** | **str** | The error message.  | [optional] 

## Example

```python
from zuora_sdk.models.fault_response import FaultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of FaultResponse from a JSON string
fault_response_instance = FaultResponse.from_json(json)
# print the JSON string representation of the object
print(FaultResponse.to_json())

# convert the object into a dict
fault_response_dict = fault_response_instance.to_dict()
# create an instance of FaultResponse from a dict
fault_response_from_dict = FaultResponse.from_dict(fault_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


