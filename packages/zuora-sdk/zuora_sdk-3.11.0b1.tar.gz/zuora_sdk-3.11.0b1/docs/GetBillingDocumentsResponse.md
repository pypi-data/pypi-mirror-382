# GetBillingDocumentsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account associated with the billing document. | [optional] 
**amount** | **float** | The total amount of the billing document. | [optional] 
**balance** | **float** | The balance of the billing document. | [optional] 
**document_date** | **date** | The date of the billing document. The date can be the invoice date for invoices, credit memo date for credit memos, or debit memo date for debit memos. | [optional] 
**document_number** | **str** | The number of the billing document. | [optional] 
**document_type** | [**BillingDocumentType**](BillingDocumentType.md) |  | [optional] 
**id** | **str** | The ID of the billing document. | [optional] 
**status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 
**currency** | **str** | The currency of the billing document. | [optional] 

## Example

```python
from zuora_sdk.models.get_billing_documents_response import GetBillingDocumentsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBillingDocumentsResponse from a JSON string
get_billing_documents_response_instance = GetBillingDocumentsResponse.from_json(json)
# print the JSON string representation of the object
print(GetBillingDocumentsResponse.to_json())

# convert the object into a dict
get_billing_documents_response_dict = get_billing_documents_response_instance.to_dict()
# create an instance of GetBillingDocumentsResponse from a dict
get_billing_documents_response_from_dict = GetBillingDocumentsResponse.from_dict(get_billing_documents_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


