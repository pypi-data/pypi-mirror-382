# ExpandedInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  | [optional] 
**adjustment_amount** | **float** |  | [optional] 
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**auto_pay** | **bool** |  | [optional] 
**balance** | **float** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**comments** | **str** |  | [optional] 
**credit_balance_adjustment_amount** | **float** |  | [optional] 
**credit_memo_amount** | **float** |  | [optional] 
**currency** | **str** |  | [optional] 
**due_date** | **date** |  | [optional] 
**includes_one_time** | **bool** |  | [optional] 
**includes_recurring** | **bool** |  | [optional] 
**includes_usage** | **bool** |  | [optional] 
**invoice_date** | **date** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**invoice_number** | **str** |  | [optional] 
**last_email_sent_date** | **str** |  | [optional] 
**organization_id** | **str** |  | [optional] 
**payment_amount** | **float** |  | [optional] 
**posted_by** | **str** |  | [optional] 
**posted_date** | **str** |  | [optional] 
**refund_amount** | **float** |  | [optional] 
**reversed** | **bool** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**sold_to_contact_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**ship_to_contact_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**source_id** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**target_date** | **date** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_exempt_amount** | **float** |  | [optional] 
**tax_status** | **str** |  | [optional] 
**tax_message** | **str** |  | [optional] 
**template_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**transferred_to_accounting** | **str** |  | [optional] 
**e_invoice_status** | **str** |  | [optional] 
**e_invoice_file_id** | **str** |  | [optional] 
**e_invoice_error_code** | **str** |  | [optional] 
**e_invoice_error_message** | **str** |  | [optional] 
**payment_link** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**bill_to_contact** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**bill_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**sold_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**ship_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**invoice_items** | [**List[ExpandedInvoiceItem]**](ExpandedInvoiceItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_invoice import ExpandedInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedInvoice from a JSON string
expanded_invoice_instance = ExpandedInvoice.from_json(json)
# print the JSON string representation of the object
print(ExpandedInvoice.to_json())

# convert the object into a dict
expanded_invoice_dict = expanded_invoice_instance.to_dict()
# create an instance of ExpandedInvoice from a dict
expanded_invoice_from_dict = ExpandedInvoice.from_dict(expanded_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


