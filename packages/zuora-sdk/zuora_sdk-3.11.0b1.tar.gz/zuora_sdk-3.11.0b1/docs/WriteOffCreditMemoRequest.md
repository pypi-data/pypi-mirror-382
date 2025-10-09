# WriteOffCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the debit memo.  | [optional] 
**memo_date** | **date** | The creation date of the debit memo and the effective date of the credit memo. Credit memos are applied to the corresponding debit memos on &#x60;memoDate&#x60;. By default, &#x60;memoDate&#x60; is set to the current date. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. The default value is &#x60;Write-off&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.write_off_credit_memo_request import WriteOffCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffCreditMemoRequest from a JSON string
write_off_credit_memo_request_instance = WriteOffCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(WriteOffCreditMemoRequest.to_json())

# convert the object into a dict
write_off_credit_memo_request_dict = write_off_credit_memo_request_instance.to_dict()
# create an instance of WriteOffCreditMemoRequest from a dict
write_off_credit_memo_request_from_dict = WriteOffCreditMemoRequest.from_dict(write_off_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


