# GetSequenceSetResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo** | [**CreditMemoEntityPrefix**](CreditMemoEntityPrefix.md) |  | [optional] 
**debit_memo** | [**DebitMemoEntityPrefix**](DebitMemoEntityPrefix.md) |  | [optional] 
**id** | **str** | The unique ID of the sequence set. For example, 402892c74c9193cd014c96bbe7c101f9. | [optional] 
**invoice** | [**InvoiceEntityPrefix**](InvoiceEntityPrefix.md) |  | [optional] 
**name** | **str** | The name of the sequence set.  | [optional] 
**payment** | [**PaymentEntityPrefix**](PaymentEntityPrefix.md) |  | [optional] 
**refund** | [**RefundEntityPrefix**](RefundEntityPrefix.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_sequence_set_response import GetSequenceSetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSequenceSetResponse from a JSON string
get_sequence_set_response_instance = GetSequenceSetResponse.from_json(json)
# print the JSON string representation of the object
print(GetSequenceSetResponse.to_json())

# convert the object into a dict
get_sequence_set_response_dict = get_sequence_set_response_instance.to_dict()
# create an instance of GetSequenceSetResponse from a dict
get_sequence_set_response_from_dict = GetSequenceSetResponse.from_dict(get_sequence_set_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


