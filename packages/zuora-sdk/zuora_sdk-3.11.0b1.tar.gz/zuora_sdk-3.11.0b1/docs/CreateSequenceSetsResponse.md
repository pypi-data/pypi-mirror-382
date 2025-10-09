# CreateSequenceSetsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sequence_sets** | [**List[GetSequenceSetResponse]**](GetSequenceSetResponse.md) | Array of sequence sets configured for billing documents, payments, and refunds. | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.create_sequence_sets_response import CreateSequenceSetsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSequenceSetsResponse from a JSON string
create_sequence_sets_response_instance = CreateSequenceSetsResponse.from_json(json)
# print the JSON string representation of the object
print(CreateSequenceSetsResponse.to_json())

# convert the object into a dict
create_sequence_sets_response_dict = create_sequence_sets_response_instance.to_dict()
# create an instance of CreateSequenceSetsResponse from a dict
create_sequence_sets_response_from_dict = CreateSequenceSetsResponse.from_dict(create_sequence_sets_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


