# GenerateBillingDocumentResponseInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the generated invoice.  | [optional] 

## Example

```python
from zuora_sdk.models.generate_billing_document_response_invoice import GenerateBillingDocumentResponseInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of GenerateBillingDocumentResponseInvoice from a JSON string
generate_billing_document_response_invoice_instance = GenerateBillingDocumentResponseInvoice.from_json(json)
# print the JSON string representation of the object
print(GenerateBillingDocumentResponseInvoice.to_json())

# convert the object into a dict
generate_billing_document_response_invoice_dict = generate_billing_document_response_invoice_instance.to_dict()
# create an instance of GenerateBillingDocumentResponseInvoice from a dict
generate_billing_document_response_invoice_from_dict = GenerateBillingDocumentResponseInvoice.from_dict(generate_billing_document_response_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


