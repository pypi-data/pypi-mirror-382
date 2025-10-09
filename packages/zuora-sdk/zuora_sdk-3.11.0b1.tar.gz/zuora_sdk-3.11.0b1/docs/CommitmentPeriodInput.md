# CommitmentPeriodInput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the period. | 
**start_date** | **date** | The start date of the period. | 
**end_date** | **date** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date | 

## Example

```python
from zuora_sdk.models.commitment_period_input import CommitmentPeriodInput

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentPeriodInput from a JSON string
commitment_period_input_instance = CommitmentPeriodInput.from_json(json)
# print the JSON string representation of the object
print(CommitmentPeriodInput.to_json())

# convert the object into a dict
commitment_period_input_dict = commitment_period_input_instance.to_dict()
# create an instance of CommitmentPeriodInput from a dict
commitment_period_input_from_dict = CommitmentPeriodInput.from_dict(commitment_period_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


