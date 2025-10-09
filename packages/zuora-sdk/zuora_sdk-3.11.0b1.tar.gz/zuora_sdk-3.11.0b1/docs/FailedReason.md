# FailedReason


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code of response.  | [optional] 
**message** | **str** | The detail information of the error response  | [optional] 

## Example

```python
from zuora_sdk.models.failed_reason import FailedReason

# TODO update the JSON string below
json = "{}"
# create an instance of FailedReason from a JSON string
failed_reason_instance = FailedReason.from_json(json)
# print the JSON string representation of the object
print(FailedReason.to_json())

# convert the object into a dict
failed_reason_dict = failed_reason_instance.to_dict()
# create an instance of FailedReason from a dict
failed_reason_from_dict = FailedReason.from_dict(failed_reason_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


