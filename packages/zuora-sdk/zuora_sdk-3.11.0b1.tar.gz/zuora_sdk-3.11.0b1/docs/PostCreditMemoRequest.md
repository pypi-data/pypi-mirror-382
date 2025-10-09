# PostCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo_date** | **date** | The new memo date when posting the credit memo. By default, it will use current memo date of the credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.post_credit_memo_request import PostCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostCreditMemoRequest from a JSON string
post_credit_memo_request_instance = PostCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(PostCreditMemoRequest.to_json())

# convert the object into a dict
post_credit_memo_request_dict = post_credit_memo_request_instance.to_dict()
# create an instance of PostCreditMemoRequest from a dict
post_credit_memo_request_from_dict = PostCreditMemoRequest.from_dict(post_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


