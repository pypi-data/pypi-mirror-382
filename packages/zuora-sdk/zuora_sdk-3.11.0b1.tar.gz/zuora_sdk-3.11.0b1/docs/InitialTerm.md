# InitialTerm

Information about the first term of the subscription. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **int** | Duration of the first term in months, years, days, or weeks, depending on the value of the &#x60;periodType&#x60; field. Only applicable if the value of the &#x60;termType&#x60; field is &#x60;TERMED&#x60;.  | [optional] 
**period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 
**start_date** | **date** | Start date of the first term, in YYYY-MM-DD format.  | [optional] 
**end_date** | **date** | End date of the first term, in YYYY-MM-DD format.  | [optional] 
**term_type** | [**TermType**](TermType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.initial_term import InitialTerm

# TODO update the JSON string below
json = "{}"
# create an instance of InitialTerm from a JSON string
initial_term_instance = InitialTerm.from_json(json)
# print the JSON string representation of the object
print(InitialTerm.to_json())

# convert the object into a dict
initial_term_dict = initial_term_instance.to_dict()
# create an instance of InitialTerm from a dict
initial_term_from_dict = InitialTerm.from_dict(initial_term_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


