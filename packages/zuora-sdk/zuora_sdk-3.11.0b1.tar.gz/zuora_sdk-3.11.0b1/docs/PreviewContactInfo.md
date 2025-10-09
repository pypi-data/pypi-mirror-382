# PreviewContactInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**city** | **str** |  | [optional] 
**country** | **str** | Country; must be a valid country name or abbreviation. If using Zuora Tax, you must specify a country to calculate tax. | [optional] 
**county** | **str** |  | [optional] 
**postal_code** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**tax_region** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_contact_info import PreviewContactInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewContactInfo from a JSON string
preview_contact_info_instance = PreviewContactInfo.from_json(json)
# print the JSON string representation of the object
print(PreviewContactInfo.to_json())

# convert the object into a dict
preview_contact_info_dict = preview_contact_info_instance.to_dict()
# create an instance of PreviewContactInfo from a dict
preview_contact_info_from_dict = PreviewContactInfo.from_dict(preview_contact_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


