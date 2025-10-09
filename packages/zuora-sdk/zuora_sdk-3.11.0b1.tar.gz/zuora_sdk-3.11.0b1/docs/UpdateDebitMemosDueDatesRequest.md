# UpdateDebitMemosDueDatesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memos** | [**List[DebitMemoDueDate]**](DebitMemoDueDate.md) | Container for debit memo update details.  | [optional] 

## Example

```python
from zuora_sdk.models.update_debit_memos_due_dates_request import UpdateDebitMemosDueDatesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateDebitMemosDueDatesRequest from a JSON string
update_debit_memos_due_dates_request_instance = UpdateDebitMemosDueDatesRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateDebitMemosDueDatesRequest.to_json())

# convert the object into a dict
update_debit_memos_due_dates_request_dict = update_debit_memos_due_dates_request_instance.to_dict()
# create an instance of UpdateDebitMemosDueDatesRequest from a dict
update_debit_memos_due_dates_request_from_dict = UpdateDebitMemosDueDatesRequest.from_dict(update_debit_memos_due_dates_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


