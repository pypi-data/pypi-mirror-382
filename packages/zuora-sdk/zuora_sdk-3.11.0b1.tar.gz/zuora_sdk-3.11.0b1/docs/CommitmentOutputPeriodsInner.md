# CommitmentOutputPeriodsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the period. | [optional] 
**start_date** | **str** | The start date of the period. | [optional] 
**end_date** | **str** | The end date of the period. The period end date is inclusive in the period, same as the commitment end date. | [optional] 
**amount** | **float** | The amount of the period. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_output_periods_inner import CommitmentOutputPeriodsInner

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentOutputPeriodsInner from a JSON string
commitment_output_periods_inner_instance = CommitmentOutputPeriodsInner.from_json(json)
# print the JSON string representation of the object
print(CommitmentOutputPeriodsInner.to_json())

# convert the object into a dict
commitment_output_periods_inner_dict = commitment_output_periods_inner_instance.to_dict()
# create an instance of CommitmentOutputPeriodsInner from a dict
commitment_output_periods_inner_from_dict = CommitmentOutputPeriodsInner.from_dict(commitment_output_periods_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


