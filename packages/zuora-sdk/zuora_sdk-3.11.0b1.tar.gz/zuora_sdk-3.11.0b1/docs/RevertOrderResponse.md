# RevertOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**account_number** | **str** | The account number for the order. | [optional] 
**subscription_numbers** | **List[str]** | The subscriptionNumber on which revert is applied. | [optional] 
**order_number** | **str** | The order number of the order created(reverting order). | [optional] 
**status** | **str** | Status of the order. &#x60;Completed&#x60; is only valid value. | [optional] 

## Example

```python
from zuora_sdk.models.revert_order_response import RevertOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RevertOrderResponse from a JSON string
revert_order_response_instance = RevertOrderResponse.from_json(json)
# print the JSON string representation of the object
print(RevertOrderResponse.to_json())

# convert the object into a dict
revert_order_response_dict = revert_order_response_instance.to_dict()
# create an instance of RevertOrderResponse from a dict
revert_order_response_from_dict = RevertOrderResponse.from_dict(revert_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


