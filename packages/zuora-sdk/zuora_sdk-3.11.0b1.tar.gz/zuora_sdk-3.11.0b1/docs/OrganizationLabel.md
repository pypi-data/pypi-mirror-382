# OrganizationLabel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** | Organization ID  | [optional] 
**organization_name** | **str** | Organization Name  | [optional] 
**cascading_down** | **bool** | Cascading down  | [optional] 
**excluded** | **bool** | Excluded  | [optional] 

## Example

```python
from zuora_sdk.models.organization_label import OrganizationLabel

# TODO update the JSON string below
json = "{}"
# create an instance of OrganizationLabel from a JSON string
organization_label_instance = OrganizationLabel.from_json(json)
# print the JSON string representation of the object
print(OrganizationLabel.to_json())

# convert the object into a dict
organization_label_dict = organization_label_instance.to_dict()
# create an instance of OrganizationLabel from a dict
organization_label_from_dict = OrganizationLabel.from_dict(organization_label_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


