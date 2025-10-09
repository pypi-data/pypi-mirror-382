# GetAccountingPeriodsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_periods** | [**List[GetAccountingPeriodWithoutSuccessResponse]**](GetAccountingPeriodWithoutSuccessResponse.md) | An array of all accounting periods on your tenant. The accounting periods are returned in ascending order of start date; that is, the latest period is returned first. | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_accounting_periods_response import GetAccountingPeriodsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountingPeriodsResponse from a JSON string
get_accounting_periods_response_instance = GetAccountingPeriodsResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountingPeriodsResponse.to_json())

# convert the object into a dict
get_accounting_periods_response_dict = get_accounting_periods_response_instance.to_dict()
# create an instance of GetAccountingPeriodsResponse from a dict
get_accounting_periods_response_from_dict = GetAccountingPeriodsResponse.from_dict(get_accounting_periods_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


