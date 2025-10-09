# GetSequenceSetsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sequence_sets** | [**List[GetSequenceSetResponse]**](GetSequenceSetResponse.md) | Array of sequence sets configured for billing documents, payments, and refunds. | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.get_sequence_sets_response import GetSequenceSetsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSequenceSetsResponse from a JSON string
get_sequence_sets_response_instance = GetSequenceSetsResponse.from_json(json)
# print the JSON string representation of the object
print(GetSequenceSetsResponse.to_json())

# convert the object into a dict
get_sequence_sets_response_dict = get_sequence_sets_response_instance.to_dict()
# create an instance of GetSequenceSetsResponse from a dict
get_sequence_sets_response_from_dict = GetSequenceSetsResponse.from_dict(get_sequence_sets_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


