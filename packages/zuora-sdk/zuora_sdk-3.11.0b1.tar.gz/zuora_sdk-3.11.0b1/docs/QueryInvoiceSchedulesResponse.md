# QueryInvoiceSchedulesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedInvoiceSchedule]**](ExpandedInvoiceSchedule.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_invoice_schedules_response import QueryInvoiceSchedulesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryInvoiceSchedulesResponse from a JSON string
query_invoice_schedules_response_instance = QueryInvoiceSchedulesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryInvoiceSchedulesResponse.to_json())

# convert the object into a dict
query_invoice_schedules_response_dict = query_invoice_schedules_response_instance.to_dict()
# create an instance of QueryInvoiceSchedulesResponse from a dict
query_invoice_schedules_response_from_dict = QueryInvoiceSchedulesResponse.from_dict(query_invoice_schedules_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


