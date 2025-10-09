# RenewalTerm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **int** | Duration of the renewal term in months, years, days, or weeks, depending on the value of the &#x60;periodType&#x60; field.  | [optional] 
**period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.renewal_term import RenewalTerm

# TODO update the JSON string below
json = "{}"
# create an instance of RenewalTerm from a JSON string
renewal_term_instance = RenewalTerm.from_json(json)
# print the JSON string representation of the object
print(RenewalTerm.to_json())

# convert the object into a dict
renewal_term_dict = renewal_term_instance.to_dict()
# create an instance of RenewalTerm from a dict
renewal_term_from_dict = RenewalTerm.from_dict(renewal_term_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


