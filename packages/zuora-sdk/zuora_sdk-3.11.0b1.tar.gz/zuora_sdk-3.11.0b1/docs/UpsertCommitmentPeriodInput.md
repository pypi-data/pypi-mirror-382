# UpsertCommitmentPeriodInput

Upsert an period, when the action is create, create a new period, when the action is update, update the period

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the period. | 
**start_date** | **date** | The start date of the period. | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | 
**action** | [**ActionType**](ActionType.md) |  | 
**id** | **str** | The ID of the period. | 

## Example

```python
from zuora_sdk.models.upsert_commitment_period_input import UpsertCommitmentPeriodInput

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCommitmentPeriodInput from a JSON string
upsert_commitment_period_input_instance = UpsertCommitmentPeriodInput.from_json(json)
# print the JSON string representation of the object
print(UpsertCommitmentPeriodInput.to_json())

# convert the object into a dict
upsert_commitment_period_input_dict = upsert_commitment_period_input_instance.to_dict()
# create an instance of UpsertCommitmentPeriodInput from a dict
upsert_commitment_period_input_from_dict = UpsertCommitmentPeriodInput.from_dict(upsert_commitment_period_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


