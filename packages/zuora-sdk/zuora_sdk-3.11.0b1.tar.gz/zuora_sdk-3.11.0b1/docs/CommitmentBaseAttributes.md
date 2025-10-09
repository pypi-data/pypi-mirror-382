# CommitmentBaseAttributes


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**commitment_number** | **str** |  | [optional] 
**name** | **str** |  | 
**type** | [**CommitmentTypeEnum**](CommitmentTypeEnum.md) |  | 
**description** | **str** |  | [optional] 
**priority** | **int** | It defines the evaluation order of the commitment, the lower the number, the higher the priority. when two commitments have the same priority, the one with the earlier created one time will be evaluated first. | [optional] 
**association_rules** | [**List[AssociationRule]**](AssociationRule.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an commitment object. | [optional] 

## Example

```python
from zuora_sdk.models.commitment_base_attributes import CommitmentBaseAttributes

# TODO update the JSON string below
json = "{}"
# create an instance of CommitmentBaseAttributes from a JSON string
commitment_base_attributes_instance = CommitmentBaseAttributes.from_json(json)
# print the JSON string representation of the object
print(CommitmentBaseAttributes.to_json())

# convert the object into a dict
commitment_base_attributes_dict = commitment_base_attributes_instance.to_dict()
# create an instance of CommitmentBaseAttributes from a dict
commitment_base_attributes_from_dict = CommitmentBaseAttributes.from_dict(commitment_base_attributes_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


