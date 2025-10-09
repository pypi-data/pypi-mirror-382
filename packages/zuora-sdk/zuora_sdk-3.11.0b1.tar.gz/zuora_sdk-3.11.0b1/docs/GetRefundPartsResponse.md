# GetRefundPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parts** | [**List[RefundPart]**](RefundPart.md) | Container for refund parts.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_refund_parts_response import GetRefundPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundPartsResponse from a JSON string
get_refund_parts_response_instance = GetRefundPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetRefundPartsResponse.to_json())

# convert the object into a dict
get_refund_parts_response_dict = get_refund_parts_response_instance.to_dict()
# create an instance of GetRefundPartsResponse from a dict
get_refund_parts_response_from_dict = GetRefundPartsResponse.from_dict(get_refund_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


