# UpsertUpdateCommitmentInput

Update the existing commitment by the commitment number.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | [**ActionType**](ActionType.md) |  | 
**commitment_number** | **str** | The number of the Commitment. | 
**name** | **str** | The value to update. Set to null to clear the existing value. | [optional] 
**description** | **str** | The value to update. Set to null to clear the existing value. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment Segment object. | [optional] 
**periods** | [**List[UpsertCommitmentPeriodInput]**](UpsertCommitmentPeriodInput.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_update_commitment_input import UpsertUpdateCommitmentInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertUpdateCommitmentInput from a JSON string
upsert_update_commitment_input_instance = UpsertUpdateCommitmentInput.from_json(json)
# print the JSON string representation of the object
print(UpsertUpdateCommitmentInput.to_json())

# convert the object into a dict
upsert_update_commitment_input_dict = upsert_update_commitment_input_instance.to_dict()
# create an instance of UpsertUpdateCommitmentInput from a dict
upsert_update_commitment_input_from_dict = UpsertUpdateCommitmentInput.from_dict(upsert_update_commitment_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


