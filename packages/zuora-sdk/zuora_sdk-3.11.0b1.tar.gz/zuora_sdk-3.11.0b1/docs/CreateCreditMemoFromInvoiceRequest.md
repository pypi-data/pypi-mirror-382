# CreateCreditMemoFromInvoiceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the credit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the credit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**transaction__ns** | **str** | Related transaction in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**auto_apply_to_invoice_upon_posting** | **bool** | Whether the credit memo automatically applies to the invoice upon posting. | [optional] 
**auto_post** | **bool** | Whether to automatically post the credit memo after it is created.  Setting this field to &#x60;true&#x60;, you do not need to separately call the [Post credit memo](https://www.zuora.com/developer/api-references/api/operation/Put_PostCreditMemo) operation to post the credit memo.  | [optional] [default to False]
**comment** | **str** | Comments about the credit memo. | [optional] 
**effective_date** | **date** | The date when the credit memo takes effect. | [optional] 
**exclude_from_auto_apply_rules** | **bool** | Whether the credit memo is excluded from the rule of automatically applying credit memos to invoices. | [optional] 
**invoice_id** | **str** | The ID of the invoice that the credit memo is created from. * If this field is specified, its value must be the same as the value of the &#x60;invoiceId&#x60; path parameter. Otherwise, its value overrides the value of the &#x60;invoiceId&#x60; path parameter.  * If this field is not specified, the value of the &#x60;invoiceId&#x60; path parameter is used.  | [optional] 
**items** | [**List[CreditMemoItemFromInvoiceItem]**](CreditMemoItemFromInvoiceItem.md) | Container for items. The maximum number of items is 1,000. | 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code. | [optional] 
**tax_auto_calculation** | **bool** | Whether to automatically calculate taxes in the credit memo. | [optional] [default to True]

## Example

```python
from zuora_sdk.models.create_credit_memo_from_invoice_request import CreateCreditMemoFromInvoiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCreditMemoFromInvoiceRequest from a JSON string
create_credit_memo_from_invoice_request_instance = CreateCreditMemoFromInvoiceRequest.from_json(json)
# print the JSON string representation of the object
print(CreateCreditMemoFromInvoiceRequest.to_json())

# convert the object into a dict
create_credit_memo_from_invoice_request_dict = create_credit_memo_from_invoice_request_instance.to_dict()
# create an instance of CreateCreditMemoFromInvoiceRequest from a dict
create_credit_memo_from_invoice_request_from_dict = CreateCreditMemoFromInvoiceRequest.from_dict(create_credit_memo_from_invoice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


