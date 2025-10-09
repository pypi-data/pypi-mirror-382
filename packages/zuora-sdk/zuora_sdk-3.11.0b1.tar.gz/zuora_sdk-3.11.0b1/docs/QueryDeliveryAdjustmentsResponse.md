# QueryDeliveryAdjustmentsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedDeliveryAdjustment]**](ExpandedDeliveryAdjustment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_delivery_adjustments_response import QueryDeliveryAdjustmentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryDeliveryAdjustmentsResponse from a JSON string
query_delivery_adjustments_response_instance = QueryDeliveryAdjustmentsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryDeliveryAdjustmentsResponse.to_json())

# convert the object into a dict
query_delivery_adjustments_response_dict = query_delivery_adjustments_response_instance.to_dict()
# create an instance of QueryDeliveryAdjustmentsResponse from a dict
query_delivery_adjustments_response_from_dict = QueryDeliveryAdjustmentsResponse.from_dict(query_delivery_adjustments_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


