# DebitMemoTaxationItemWriteOffRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**taxation_item_id** | **str** | The ID of the debit memo item.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_taxation_item_write_off_request import DebitMemoTaxationItemWriteOffRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoTaxationItemWriteOffRequest from a JSON string
debit_memo_taxation_item_write_off_request_instance = DebitMemoTaxationItemWriteOffRequest.from_json(json)
# print the JSON string representation of the object
print(DebitMemoTaxationItemWriteOffRequest.to_json())

# convert the object into a dict
debit_memo_taxation_item_write_off_request_dict = debit_memo_taxation_item_write_off_request_instance.to_dict()
# create an instance of DebitMemoTaxationItemWriteOffRequest from a dict
debit_memo_taxation_item_write_off_request_from_dict = DebitMemoTaxationItemWriteOffRequest.from_dict(debit_memo_taxation_item_write_off_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


