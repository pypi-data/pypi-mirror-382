# FulfillmentItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Fulfillment Item object.  | [optional] 
**description** | **str** | The description of the Fulfillment Item.  | [optional] 
**item_identifier** | **str** | The external identifier of the Fulfillment Item.  | [optional] 
**fulfillment_id** | **str** | The fulfillment Id of the Fulfillment Item.  | [optional] 
**fulfillment_external_id** | **str** | The fulfillmentExternalId of the Fulfillment Item.  | [optional] 

## Example

```python
from zuora_sdk.models.fulfillment_item import FulfillmentItem

# TODO update the JSON string below
json = "{}"
# create an instance of FulfillmentItem from a JSON string
fulfillment_item_instance = FulfillmentItem.from_json(json)
# print the JSON string representation of the object
print(FulfillmentItem.to_json())

# convert the object into a dict
fulfillment_item_dict = fulfillment_item_instance.to_dict()
# create an instance of FulfillmentItem from a dict
fulfillment_item_from_dict = FulfillmentItem.from_dict(fulfillment_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


