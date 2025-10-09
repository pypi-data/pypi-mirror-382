# CreateSequenceSetsRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sequence_sets** | [**List[CreateSequenceSetRequest]**](CreateSequenceSetRequest.md) | Array of sequence sets configured for billing documents, payments, and refunds. | [optional] 

## Example

```python
from zuora_sdk.models.create_sequence_sets_request import CreateSequenceSetsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSequenceSetsRequest from a JSON string
create_sequence_sets_request_instance = CreateSequenceSetsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateSequenceSetsRequest.to_json())

# convert the object into a dict
create_sequence_sets_request_dict = create_sequence_sets_request_instance.to_dict()
# create an instance of CreateSequenceSetsRequest from a dict
create_sequence_sets_request_from_dict = CreateSequenceSetsRequest.from_dict(create_sequence_sets_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


