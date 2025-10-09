# UpdateSequenceSetRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo** | [**CreditMemoEntityPrefix**](CreditMemoEntityPrefix.md) |  | [optional] 
**debit_memo** | [**DebitMemoEntityPrefix**](DebitMemoEntityPrefix.md) |  | [optional] 
**invoice** | [**InvoiceEntityPrefix**](InvoiceEntityPrefix.md) |  | [optional] 
**name** | **str** | The name of the sequence set configured for billing documents, payments, and refunds. | [optional] 
**payment** | [**PaymentEntityPrefix**](PaymentEntityPrefix.md) |  | [optional] 
**refund** | [**RefundEntityPrefix**](RefundEntityPrefix.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_sequence_set_request import UpdateSequenceSetRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSequenceSetRequest from a JSON string
update_sequence_set_request_instance = UpdateSequenceSetRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateSequenceSetRequest.to_json())

# convert the object into a dict
update_sequence_set_request_dict = update_sequence_set_request_instance.to_dict()
# create an instance of UpdateSequenceSetRequest from a dict
update_sequence_set_request_from_dict = UpdateSequenceSetRequest.from_dict(update_sequence_set_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


