# GetDebitMemoApplicationPart


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_amount** | **float** | The amount that is applied to the debit memo.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the payment or credit memo.  | [optional] 
**created_date** | **str** | The date and time when the payment or credit memo was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-12-01 15:31:10. | [optional] 
**credit_memo_id** | **str** | The ID of credit memo that is applied to the specified debit memo.  | [optional] 
**payment_id** | **str** | The ID of the payment that is applied to the specified debit memo.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the payment or credit memo.  | [optional] 
**updated_date** | **str** | The date and time when the payment or credit memo was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2018-01-02 11:42:16. | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_application_part import GetDebitMemoApplicationPart

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoApplicationPart from a JSON string
get_debit_memo_application_part_instance = GetDebitMemoApplicationPart.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoApplicationPart.to_json())

# convert the object into a dict
get_debit_memo_application_part_dict = get_debit_memo_application_part_instance.to_dict()
# create an instance of GetDebitMemoApplicationPart from a dict
get_debit_memo_application_part_from_dict = GetDebitMemoApplicationPart.from_dict(get_debit_memo_application_part_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


