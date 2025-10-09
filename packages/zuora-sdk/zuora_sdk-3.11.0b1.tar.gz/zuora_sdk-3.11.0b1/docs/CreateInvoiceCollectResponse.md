# CreateInvoiceCollectResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount_collected** | **decimal.Decimal** | Payment amount applied.  | [optional] 
**credit_memos** | [**List[CreateInvoiceCollectCreditMemos]**](CreateInvoiceCollectCreditMemos.md) | Information on one or more credit memos associated with this operation.  | [optional] 
**invoices** | [**List[CreateInvoiceCollectInvoices]**](CreateInvoiceCollectInvoices.md) | Information on one or more invoices associated with this operation.  | [optional] 
**payment_id** | **str** | Payment ID.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_collect_response import CreateInvoiceCollectResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceCollectResponse from a JSON string
create_invoice_collect_response_instance = CreateInvoiceCollectResponse.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceCollectResponse.to_json())

# convert the object into a dict
create_invoice_collect_response_dict = create_invoice_collect_response_instance.to_dict()
# create an instance of CreateInvoiceCollectResponse from a dict
create_invoice_collect_response_from_dict = CreateInvoiceCollectResponse.from_dict(create_invoice_collect_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


