# CreateSequenceSetRequest



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo** | [**CreditMemoEntityPrefix**](CreditMemoEntityPrefix.md) |  | 
**debit_memo** | [**DebitMemoEntityPrefix**](DebitMemoEntityPrefix.md) |  | 
**invoice** | [**InvoiceEntityPrefix**](InvoiceEntityPrefix.md) |  | 
**name** | **str** | The name of the sequence set to configure for billing documents, payments, and refunds. | 
**payment** | [**PaymentEntityPrefix**](PaymentEntityPrefix.md) |  | [optional] 
**refund** | [**RefundEntityPrefix**](RefundEntityPrefix.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_sequence_set_request import CreateSequenceSetRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSequenceSetRequest from a JSON string
create_sequence_set_request_instance = CreateSequenceSetRequest.from_json(json)
# print the JSON string representation of the object
print(CreateSequenceSetRequest.to_json())

# convert the object into a dict
create_sequence_set_request_dict = create_sequence_set_request_instance.to_dict()
# create an instance of CreateSequenceSetRequest from a dict
create_sequence_set_request_from_dict = CreateSequenceSetRequest.from_dict(create_sequence_set_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


