# GetFulfillmentItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Fulfillment Item object.  | [optional] 
**description** | **str** | The description of the Fulfillment Item.  | [optional] 
**item_identifier** | **str** | The external identifier of the Fulfillment Item.  | [optional] 
**fulfillment_id** | **str** | The reference id of the related Fulfillment.  | [optional] 
**fulfillment_external_id** | **str** | The fulfillmentExternalId of the Fulfillment Item.  | [optional] 
**id** | **str** | The sytem generated Id.  | [optional] 

## Example

```python
from zuora_sdk.models.get_fulfillment_item import GetFulfillmentItem

# TODO update the JSON string below
json = "{}"
# create an instance of GetFulfillmentItem from a JSON string
get_fulfillment_item_instance = GetFulfillmentItem.from_json(json)
# print the JSON string representation of the object
print(GetFulfillmentItem.to_json())

# convert the object into a dict
get_fulfillment_item_dict = get_fulfillment_item_instance.to_dict()
# create an instance of GetFulfillmentItem from a dict
get_fulfillment_item_from_dict = GetFulfillmentItem.from_dict(get_fulfillment_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


