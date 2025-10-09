# GenerateBillingDocumentResponseCreditMemo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the generated credit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.generate_billing_document_response_credit_memo import GenerateBillingDocumentResponseCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of GenerateBillingDocumentResponseCreditMemo from a JSON string
generate_billing_document_response_credit_memo_instance = GenerateBillingDocumentResponseCreditMemo.from_json(json)
# print the JSON string representation of the object
print(GenerateBillingDocumentResponseCreditMemo.to_json())

# convert the object into a dict
generate_billing_document_response_credit_memo_dict = generate_billing_document_response_credit_memo_instance.to_dict()
# create an instance of GenerateBillingDocumentResponseCreditMemo from a dict
generate_billing_document_response_credit_memo_from_dict = GenerateBillingDocumentResponseCreditMemo.from_dict(generate_billing_document_response_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


