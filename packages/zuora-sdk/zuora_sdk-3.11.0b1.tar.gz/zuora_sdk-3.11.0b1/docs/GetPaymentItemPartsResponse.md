# GetPaymentItemPartsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**parts** | [**List[PaymentItemPart]**](PaymentItemPart.md) | Container for payment part items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_item_parts_response import GetPaymentItemPartsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentItemPartsResponse from a JSON string
get_payment_item_parts_response_instance = GetPaymentItemPartsResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentItemPartsResponse.to_json())

# convert the object into a dict
get_payment_item_parts_response_dict = get_payment_item_parts_response_instance.to_dict()
# create an instance of GetPaymentItemPartsResponse from a dict
get_payment_item_parts_response_from_dict = GetPaymentItemPartsResponse.from_dict(get_payment_item_parts_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


