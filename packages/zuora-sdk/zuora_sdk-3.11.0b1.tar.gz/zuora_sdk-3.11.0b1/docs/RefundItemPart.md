# RefundItemPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the refund part item.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the refund part item.  | [optional] 
**created_date** | **str** | The date and time when the refund part item was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_memo_item_id** | **str** | The ID of the credit memo item associated with the refund part item.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item associated with the refund part item. | [optional] 
**id** | **str** | The ID of the refund part item.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the refund part item.  | [optional] 
**updated_date** | **str** | The date and time when the refund part item was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.refund_item_part import RefundItemPart

# TODO update the JSON string below
json = "{}"
# create an instance of RefundItemPart from a JSON string
refund_item_part_instance = RefundItemPart.from_json(json)
# print the JSON string representation of the object
print(RefundItemPart.to_json())

# convert the object into a dict
refund_item_part_dict = refund_item_part_instance.to_dict()
# create an instance of RefundItemPart from a dict
refund_item_part_from_dict = RefundItemPart.from_dict(refund_item_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


