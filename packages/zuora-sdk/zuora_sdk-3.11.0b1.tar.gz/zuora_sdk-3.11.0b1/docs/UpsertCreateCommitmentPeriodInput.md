# UpsertCreateCommitmentPeriodInput

Create a new period.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the period. | 
**start_date** | **date** | The start date of the period. | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | 
**action** | [**ActionType**](ActionType.md) |  | 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_period_input import UpsertCreateCommitmentPeriodInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentPeriodInput from a JSON string
upsert_create_commitment_period_input_instance = UpsertCreateCommitmentPeriodInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentPeriodInput.to_json())

# convert the object into a dict
upsert_create_commitment_period_input_dict = upsert_create_commitment_period_input_instance.to_dict()
# create an instance of UpsertCreateCommitmentPeriodInput from a dict
upsert_create_commitment_period_input_from_dict = UpsertCreateCommitmentPeriodInput.from_dict(upsert_create_commitment_period_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


