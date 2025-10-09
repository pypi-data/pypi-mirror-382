# RegenerateBookingRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**subscription_id** | **str** |  | [optional] 
**subscription_name** | **str** |  | [optional] 
**subscription_version** | **int** |  | [optional] 
**order_line_item_id** | **str** |  | [optional] 
**order_number** | **str** |  | [optional] 
**item_number** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.regenerate_booking_request import RegenerateBookingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RegenerateBookingRequest from a JSON string
regenerate_booking_request_instance = RegenerateBookingRequest.from_json(json)
# print the JSON string representation of the object
print(RegenerateBookingRequest.to_json())

# convert the object into a dict
regenerate_booking_request_dict = regenerate_booking_request_instance.to_dict()
# create an instance of RegenerateBookingRequest from a dict
regenerate_booking_request_from_dict = RegenerateBookingRequest.from_dict(regenerate_booking_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


