# TermInfo

Container for the terms and renewal settings of the subscription. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_renew** | **bool** | Specifies whether the subscription automatically renews at the end of the each term. Only applicable if the type of the first term is &#x60;TERMED&#x60;.  | [optional] 
**initial_term** | [**InitialTerm**](InitialTerm.md) |  | 
**renewal_setting** | [**RenewalSetting**](RenewalSetting.md) |  | [optional] 
**renewal_terms** | [**RenewalTerm**](RenewalTerm.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.term_info import TermInfo

# TODO update the JSON string below
json = "{}"
# create an instance of TermInfo from a JSON string
term_info_instance = TermInfo.from_json(json)
# print the JSON string representation of the object
print(TermInfo.to_json())

# convert the object into a dict
term_info_dict = term_info_instance.to_dict()
# create an instance of TermInfo from a dict
term_info_from_dict = TermInfo.from_dict(term_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


