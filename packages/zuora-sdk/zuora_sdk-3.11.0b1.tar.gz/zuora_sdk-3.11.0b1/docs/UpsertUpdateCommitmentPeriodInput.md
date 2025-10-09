# UpsertUpdateCommitmentPeriodInput

Update an existing Commitment Period.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the period. | 
**action** | [**ActionType**](ActionType.md) |  | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | [optional] 

## Example

```python
from zuora_sdk.models.upsert_update_commitment_period_input import UpsertUpdateCommitmentPeriodInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertUpdateCommitmentPeriodInput from a JSON string
upsert_update_commitment_period_input_instance = UpsertUpdateCommitmentPeriodInput.from_json(json)
# print the JSON string representation of the object
print(UpsertUpdateCommitmentPeriodInput.to_json())

# convert the object into a dict
upsert_update_commitment_period_input_dict = upsert_update_commitment_period_input_instance.to_dict()
# create an instance of UpsertUpdateCommitmentPeriodInput from a dict
upsert_update_commitment_period_input_from_dict = UpsertUpdateCommitmentPeriodInput.from_dict(upsert_update_commitment_period_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


