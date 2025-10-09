# LastTerm

The length of the period for the current subscription term.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period** | **int** | Specify only when the termType is &#39;TERMED&#39;. | [optional] 
**period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 
**start_date** | **date** | The start date of the current term. You can change the term start date of a renewed subscription through a T&amp;Cs order action. However, when changing it to an earlier date, this date must not be earlier than the term start date of the current term before this T&amp;Cs.  | [optional] 
**end_date** | **date** | End date of the current term, in YYYY-MM-DD format.  | [optional] 
**term_type** | [**TermType**](TermType.md) |  | 

## Example

```python
from zuora_sdk.models.last_term import LastTerm

# TODO update the JSON string below
json = "{}"
# create an instance of LastTerm from a JSON string
last_term_instance = LastTerm.from_json(json)
# print the JSON string representation of the object
print(LastTerm.to_json())

# convert the object into a dict
last_term_dict = last_term_instance.to_dict()
# create an instance of LastTerm from a dict
last_term_from_dict = LastTerm.from_dict(last_term_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


