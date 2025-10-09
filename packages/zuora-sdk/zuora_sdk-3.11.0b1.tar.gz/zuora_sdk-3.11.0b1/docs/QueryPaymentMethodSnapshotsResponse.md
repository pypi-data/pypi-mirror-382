# QueryPaymentMethodSnapshotsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentMethodSnapshot]**](ExpandedPaymentMethodSnapshot.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_method_snapshots_response import QueryPaymentMethodSnapshotsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentMethodSnapshotsResponse from a JSON string
query_payment_method_snapshots_response_instance = QueryPaymentMethodSnapshotsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentMethodSnapshotsResponse.to_json())

# convert the object into a dict
query_payment_method_snapshots_response_dict = query_payment_method_snapshots_response_instance.to_dict()
# create an instance of QueryPaymentMethodSnapshotsResponse from a dict
query_payment_method_snapshots_response_from_dict = QueryPaymentMethodSnapshotsResponse.from_dict(query_payment_method_snapshots_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


