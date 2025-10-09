# CommitmentOutput


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**commitment_number** | **str** |  | [optional] 
**type** | [**CommitmentTypeEnum**](CommitmentTypeEnum.md) |  | [optional] 
**start_date** | **date** | The start date of the commitment. | [optional] 
**end_date** | **date** | The end date of the commitment. | [optional] 
**amount** | **float** | The total amount of the commitment. | [optional] 
**periods** | [**List[CommitmentOutputPeriodsInner]**](CommitmentOutputPeriodsInner.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.commitment_output import CommitmentOutput

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentOutput from a JSON string
commitment_output_instance = CommitmentOutput.from_json(json)
# print the JSON string representation of the object
print(CommitmentOutput.to_json())

# convert the object into a dict
commitment_output_dict = commitment_output_instance.to_dict()
# create an instance of CommitmentOutput from a dict
commitment_output_from_dict = CommitmentOutput.from_dict(commitment_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


