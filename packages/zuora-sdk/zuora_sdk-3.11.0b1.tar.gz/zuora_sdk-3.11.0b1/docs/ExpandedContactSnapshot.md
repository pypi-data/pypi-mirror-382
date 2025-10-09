# ExpandedContactSnapshot


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**address1** | **str** |  | [optional] 
**address2** | **str** |  | [optional] 
**city** | **str** |  | [optional] 
**contact_id** | **str** |  | [optional] 
**country** | **str** |  | [optional] 
**county** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**fax** | **str** |  | [optional] 
**first_name** | **str** |  | [optional] 
**home_phone** | **str** |  | [optional] 
**last_name** | **str** |  | [optional] 
**mobile_phone** | **str** |  | [optional] 
**nick_name** | **str** |  | [optional] 
**other_phone** | **str** |  | [optional] 
**other_phone_type** | **str** |  | [optional] 
**personal_email** | **str** |  | [optional] 
**postal_code** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**tax_region** | **str** |  | [optional] 
**work_email** | **str** |  | [optional] 
**work_phone** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_contact_snapshot import ExpandedContactSnapshot

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedContactSnapshot from a JSON string
expanded_contact_snapshot_instance = ExpandedContactSnapshot.from_json(json)
# print the JSON string representation of the object
print(ExpandedContactSnapshot.to_json())

# convert the object into a dict
expanded_contact_snapshot_dict = expanded_contact_snapshot_instance.to_dict()
# create an instance of ExpandedContactSnapshot from a dict
expanded_contact_snapshot_from_dict = ExpandedContactSnapshot.from_dict(expanded_contact_snapshot_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


