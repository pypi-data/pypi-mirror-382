# CreateCreditMemoTaxationItemsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**taxation_items** | [**List[CreateTaxationItemForCreditMemoRequest]**](CreateTaxationItemForCreditMemoRequest.md) | Container for taxation items.  | 

## Example

```python
from zuora_sdk.models.create_credit_memo_taxation_items_request import CreateCreditMemoTaxationItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCreditMemoTaxationItemsRequest from a JSON string
create_credit_memo_taxation_items_request_instance = CreateCreditMemoTaxationItemsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateCreditMemoTaxationItemsRequest.to_json())

# convert the object into a dict
create_credit_memo_taxation_items_request_dict = create_credit_memo_taxation_items_request_instance.to_dict()
# create an instance of CreateCreditMemoTaxationItemsRequest from a dict
create_credit_memo_taxation_items_request_from_dict = CreateCreditMemoTaxationItemsRequest.from_dict(create_credit_memo_taxation_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


