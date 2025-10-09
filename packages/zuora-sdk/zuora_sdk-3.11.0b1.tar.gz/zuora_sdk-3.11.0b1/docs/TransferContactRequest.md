# TransferContactRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**destination_account_key** | **str** | The ID or number of the destination account. | 

## Example

```python
from zuora_sdk.models.transfer_contact_request import TransferContactRequest

# TODO update the JSON string below
json = "{}"
# create an instance of TransferContactRequest from a JSON string
transfer_contact_request_instance = TransferContactRequest.from_json(json)
# print the JSON string representation of the object
print(TransferContactRequest.to_json())

# convert the object into a dict
transfer_contact_request_dict = transfer_contact_request_instance.to_dict()
# create an instance of TransferContactRequest from a dict
transfer_contact_request_from_dict = TransferContactRequest.from_dict(transfer_contact_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


