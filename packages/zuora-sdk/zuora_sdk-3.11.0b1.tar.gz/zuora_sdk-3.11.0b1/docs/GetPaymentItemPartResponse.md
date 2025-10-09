# GetPaymentItemPartResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 
**payment_item_part** | [**PaymentItemPart**](PaymentItemPart.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_item_part_response import GetPaymentItemPartResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentItemPartResponse from a JSON string
get_payment_item_part_response_instance = GetPaymentItemPartResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentItemPartResponse.to_json())

# convert the object into a dict
get_payment_item_part_response_dict = get_payment_item_part_response_instance.to_dict()
# create an instance of GetPaymentItemPartResponse from a dict
get_payment_item_part_response_from_dict = GetPaymentItemPartResponse.from_dict(get_payment_item_part_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


