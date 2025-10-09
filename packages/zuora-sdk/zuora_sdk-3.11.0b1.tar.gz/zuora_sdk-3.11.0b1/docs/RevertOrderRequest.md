# RevertOrderRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_date** | **date** | The order date when order is booked in YYYY-MM-DD format. | 

## Example

```python
from zuora_sdk.models.revert_order_request import RevertOrderRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RevertOrderRequest from a JSON string
revert_order_request_instance = RevertOrderRequest.from_json(json)
# print the JSON string representation of the object
print(RevertOrderRequest.to_json())

# convert the object into a dict
revert_order_request_dict = revert_order_request_instance.to_dict()
# create an instance of RevertOrderRequest from a dict
revert_order_request_from_dict = RevertOrderRequest.from_dict(revert_order_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


