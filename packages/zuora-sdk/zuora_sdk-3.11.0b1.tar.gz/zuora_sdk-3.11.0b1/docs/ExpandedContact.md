# ExpandedContact


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
**as_bill_to** | **bool** |  | [optional] 
**as_sold_to** | **bool** |  | [optional] 
**as_ship_to** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_contact import ExpandedContact

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedContact from a JSON string
expanded_contact_instance = ExpandedContact.from_json(json)
# print the JSON string representation of the object
print(ExpandedContact.to_json())

# convert the object into a dict
expanded_contact_dict = expanded_contact_instance.to_dict()
# create an instance of ExpandedContact from a dict
expanded_contact_from_dict = ExpandedContact.from_dict(expanded_contact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


