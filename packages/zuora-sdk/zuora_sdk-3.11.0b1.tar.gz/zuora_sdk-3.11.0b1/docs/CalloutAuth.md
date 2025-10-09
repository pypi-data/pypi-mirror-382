# CalloutAuth

If `requiredAuth` is `true`, this object is required.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**domain** | **str** | The domain of the callout auth. | [optional] 
**password** | **str** | The field is required when requiredAuth is &#x60;true&#x60;. | [optional] 
**preemptive** | **bool** | Set this field to &#x60;true&#x60; if you want to enable the preemptive authentication. | [optional] 
**username** | **str** | The field is required when requiredAuth is &#x60;true&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.callout_auth import CalloutAuth

# TODO update the JSON string below
json = "{}"
# create an instance of CalloutAuth from a JSON string
callout_auth_instance = CalloutAuth.from_json(json)
# print the JSON string representation of the object
print(CalloutAuth.to_json())

# convert the object into a dict
callout_auth_dict = callout_auth_instance.to_dict()
# create an instance of CalloutAuth from a dict
callout_auth_from_dict = CalloutAuth.from_dict(callout_auth_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


