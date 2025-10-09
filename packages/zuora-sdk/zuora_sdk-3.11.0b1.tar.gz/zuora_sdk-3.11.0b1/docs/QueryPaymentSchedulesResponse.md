# QueryPaymentSchedulesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentSchedule]**](ExpandedPaymentSchedule.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_schedules_response import QueryPaymentSchedulesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentSchedulesResponse from a JSON string
query_payment_schedules_response_instance = QueryPaymentSchedulesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentSchedulesResponse.to_json())

# convert the object into a dict
query_payment_schedules_response_dict = query_payment_schedules_response_instance.to_dict()
# create an instance of QueryPaymentSchedulesResponse from a dict
query_payment_schedules_response_from_dict = QueryPaymentSchedulesResponse.from_dict(query_payment_schedules_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


