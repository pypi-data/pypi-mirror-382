# UpsertCreateCommitmentInputAllOfPeriods


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the period. | 
**start_date** | **date** | The start date of the period. | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | 
**action** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.upsert_create_commitment_input_all_of_periods import UpsertCreateCommitmentInputAllOfPeriods

# TODO update the JSON string below
json = "{}"
# create an instance of UpsertCreateCommitmentInputAllOfPeriods from a JSON string
upsert_create_commitment_input_all_of_periods_instance = UpsertCreateCommitmentInputAllOfPeriods.from_json(json)
# print the JSON string representation of the object
print(UpsertCreateCommitmentInputAllOfPeriods.to_json())

# convert the object into a dict
upsert_create_commitment_input_all_of_periods_dict = upsert_create_commitment_input_all_of_periods_instance.to_dict()
# create an instance of UpsertCreateCommitmentInputAllOfPeriods from a dict
upsert_create_commitment_input_all_of_periods_from_dict = UpsertCreateCommitmentInputAllOfPeriods.from_dict(upsert_create_commitment_input_all_of_periods_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


