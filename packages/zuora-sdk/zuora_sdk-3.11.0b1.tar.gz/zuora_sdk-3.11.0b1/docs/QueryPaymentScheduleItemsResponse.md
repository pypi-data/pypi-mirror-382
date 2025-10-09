# QueryPaymentScheduleItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentScheduleItem]**](ExpandedPaymentScheduleItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_schedule_items_response import QueryPaymentScheduleItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentScheduleItemsResponse from a JSON string
query_payment_schedule_items_response_instance = QueryPaymentScheduleItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentScheduleItemsResponse.to_json())

# convert the object into a dict
query_payment_schedule_items_response_dict = query_payment_schedule_items_response_instance.to_dict()
# create an instance of QueryPaymentScheduleItemsResponse from a dict
query_payment_schedule_items_response_from_dict = QueryPaymentScheduleItemsResponse.from_dict(query_payment_schedule_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


