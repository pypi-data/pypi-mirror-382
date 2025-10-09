# InvoiceEntityPrefix

Container for the prefix and starting document number of invoices. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prefix** | **str** | The prefix of invoices.  | [optional] 
**start_number** | **int** | The starting document number of invoices.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_entity_prefix import InvoiceEntityPrefix

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceEntityPrefix from a JSON string
invoice_entity_prefix_instance = InvoiceEntityPrefix.from_json(json)
# print the JSON string representation of the object
print(InvoiceEntityPrefix.to_json())

# convert the object into a dict
invoice_entity_prefix_dict = invoice_entity_prefix_instance.to_dict()
# create an instance of InvoiceEntityPrefix from a dict
invoice_entity_prefix_from_dict = InvoiceEntityPrefix.from_dict(invoice_entity_prefix_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


