# UpdateOrderCustomFieldsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order object.  | [optional] 
**subscriptions** | [**List[UpdateOrderSubscriptionsCustomFields]**](UpdateOrderSubscriptionsCustomFields.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_custom_fields_request import UpdateOrderCustomFieldsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderCustomFieldsRequest from a JSON string
update_order_custom_fields_request_instance = UpdateOrderCustomFieldsRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderCustomFieldsRequest.to_json())

# convert the object into a dict
update_order_custom_fields_request_dict = update_order_custom_fields_request_instance.to_dict()
# create an instance of UpdateOrderCustomFieldsRequest from a dict
update_order_custom_fields_request_from_dict = UpdateOrderCustomFieldsRequest.from_dict(update_order_custom_fields_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


