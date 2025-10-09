# GetRefundItemPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**item_parts** | [**List[RefundItemPart]**](RefundItemPart.md) | Container for refund part items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_refund_item_parts_response import GetRefundItemPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundItemPartsResponse from a JSON string
get_refund_item_parts_response_instance = GetRefundItemPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetRefundItemPartsResponse.to_json())

# convert the object into a dict
get_refund_item_parts_response_dict = get_refund_item_parts_response_instance.to_dict()
# create an instance of GetRefundItemPartsResponse from a dict
get_refund_item_parts_response_from_dict = GetRefundItemPartsResponse.from_dict(get_refund_item_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


