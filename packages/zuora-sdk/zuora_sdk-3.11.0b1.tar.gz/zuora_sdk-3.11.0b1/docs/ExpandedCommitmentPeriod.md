# ExpandedCommitmentPeriod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**commitment_id** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**priority** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**amount** | **float** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_commitment_period import ExpandedCommitmentPeriod

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCommitmentPeriod from a JSON string
expanded_commitment_period_instance = ExpandedCommitmentPeriod.from_json(json)
# print the JSON string representation of the object
print(ExpandedCommitmentPeriod.to_json())

# convert the object into a dict
expanded_commitment_period_dict = expanded_commitment_period_instance.to_dict()
# create an instance of ExpandedCommitmentPeriod from a dict
expanded_commitment_period_from_dict = ExpandedCommitmentPeriod.from_dict(expanded_commitment_period_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


