# TransferPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account that the payment is transferred to.  Unassign a payment by setting this field to an empty string. This will automatically transfer the payment to a null account. | [optional] 

## Example

```python
from zuora_sdk.models.transfer_payment import TransferPayment

# TODO update the JSON string below
json = "{}"
# create an instance of TransferPayment from a JSON string
transfer_payment_instance = TransferPayment.from_json(json)
# print the JSON string representation of the object
print(TransferPayment.to_json())

# convert the object into a dict
transfer_payment_dict = transfer_payment_instance.to_dict()
# create an instance of TransferPayment from a dict
transfer_payment_from_dict = TransferPayment.from_dict(transfer_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


