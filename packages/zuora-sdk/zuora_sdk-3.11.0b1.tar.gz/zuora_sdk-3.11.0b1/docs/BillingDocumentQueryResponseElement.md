# BillingDocumentQueryResponseElement


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**List[GetBillingDocumentsResponse]**](GetBillingDocumentsResponse.md) | Container for billing documents.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.billing_document_query_response_element import BillingDocumentQueryResponseElement

# TODO update the JSON string below
json = "{}"
# create an instance of BillingDocumentQueryResponseElement from a JSON string
billing_document_query_response_element_instance = BillingDocumentQueryResponseElement.from_json(json)
# print the JSON string representation of the object
print(BillingDocumentQueryResponseElement.to_json())

# convert the object into a dict
billing_document_query_response_element_dict = billing_document_query_response_element_instance.to_dict()
# create an instance of BillingDocumentQueryResponseElement from a dict
billing_document_query_response_element_from_dict = BillingDocumentQueryResponseElement.from_dict(billing_document_query_response_element_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


