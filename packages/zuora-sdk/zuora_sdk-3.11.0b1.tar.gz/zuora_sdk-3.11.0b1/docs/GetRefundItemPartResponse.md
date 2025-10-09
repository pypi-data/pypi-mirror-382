# GetRefundItemPartResponse


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
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]

## Example

```python
from zuora_sdk.models.get_refund_item_part_response import GetRefundItemPartResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundItemPartResponse from a JSON string
get_refund_item_part_response_instance = GetRefundItemPartResponse.from_json(json)
# print the JSON string representation of the object
print(GetRefundItemPartResponse.to_json())

# convert the object into a dict
get_refund_item_part_response_dict = get_refund_item_part_response_instance.to_dict()
# create an instance of GetRefundItemPartResponse from a dict
get_refund_item_part_response_from_dict = GetRefundItemPartResponse.from_dict(get_refund_item_part_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


