# GetRefundPartResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the refund part.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the refund part.  | [optional] 
**created_date** | **str** | The date and time when the refund part was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**credit_memo_id** | **str** | The ID of the credit memo associated with the refund part.  | [optional] 
**id** | **str** | The ID of the refund part.  | [optional] 
**payment_id** | **str** | The ID of the payment associated with the refund part.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the refund part.  | [optional] 
**updated_date** | **str** | The date and time when the refund part was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10. | [optional] 
**organization_label** | **str** |  | [optional] 
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]

## Example

```python
from zuora_sdk.models.get_refund_part_response import GetRefundPartResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundPartResponse from a JSON string
get_refund_part_response_instance = GetRefundPartResponse.from_json(json)
# print the JSON string representation of the object
print(GetRefundPartResponse.to_json())

# convert the object into a dict
get_refund_part_response_dict = get_refund_part_response_instance.to_dict()
# create an instance of GetRefundPartResponse from a dict
get_refund_part_response_from_dict = GetRefundPartResponse.from_dict(get_refund_part_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


