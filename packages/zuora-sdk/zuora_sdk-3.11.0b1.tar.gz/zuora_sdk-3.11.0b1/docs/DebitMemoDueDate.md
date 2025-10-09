# DebitMemoDueDate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**due_date** | **date** | The date by which the payment for the debit memo is due, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**id** | **str** | The unique ID or number of the debit memo to be updated. For example, 402890555a87d7f5015a892f2ba10057 or or DM00000001. | [optional] 
**memo_key** | **str** | The unique ID or number of the debit memo to be updated. For example, 402890555a87d7f5015a892f2ba10057 or or DM00000001. If &#x60;memoKey&#x60; is set, &#x60;id&#x60; will be ignored. | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_due_date import DebitMemoDueDate

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoDueDate from a JSON string
debit_memo_due_date_instance = DebitMemoDueDate.from_json(json)
# print the JSON string representation of the object
print(DebitMemoDueDate.to_json())

# convert the object into a dict
debit_memo_due_date_dict = debit_memo_due_date_instance.to_dict()
# create an instance of DebitMemoDueDate from a dict
debit_memo_due_date_from_dict = DebitMemoDueDate.from_dict(debit_memo_due_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


