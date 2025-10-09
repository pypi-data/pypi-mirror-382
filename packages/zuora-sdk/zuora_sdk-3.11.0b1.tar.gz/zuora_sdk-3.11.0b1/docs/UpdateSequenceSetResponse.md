# UpdateSequenceSetResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.update_sequence_set_response import UpdateSequenceSetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSequenceSetResponse from a JSON string
update_sequence_set_response_instance = UpdateSequenceSetResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateSequenceSetResponse.to_json())

# convert the object into a dict
update_sequence_set_response_dict = update_sequence_set_response_instance.to_dict()
# create an instance of UpdateSequenceSetResponse from a dict
update_sequence_set_response_from_dict = UpdateSequenceSetResponse.from_dict(update_sequence_set_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


