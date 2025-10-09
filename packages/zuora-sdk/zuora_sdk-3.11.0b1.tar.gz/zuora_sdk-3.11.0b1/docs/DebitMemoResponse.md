# DebitMemoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**account_id** | **str** | The ID of the customer account associated with the debit memo. | [optional] 
**account_number** | **str** | The number of the customer account associated with the debit memo. | [optional] 
**amount** | **float** | The total amount of the debit memo. | [optional] 
**auto_pay** | **bool** | Whether debit memos are automatically picked up for processing in the corresponding payment run.   By default, debit memos are automatically picked up for processing in the corresponding payment run.        | [optional] 
**balance** | **float** | The balance of the debit memo. | [optional] 
**be_applied_amount** | **float** | The applied amount of the debit memo. | [optional] 
**bill_to_contact_id** | **str** | The ID of the bill-to contact associated with the debit memo.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**cancelled_by_id** | **str** | The ID of the Zuora user who cancelled the debit memo. | [optional] 
**cancelled_on** | **str** | The date and time when the debit memo was cancelled, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**comment** | **str** | Comments about the debit memo. | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the debit memo. | [optional] 
**created_date** | **str** | The date and time when the debit memo was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10. | [optional] 
**debit_memo_date** | **date** | The date when the debit memo takes effect, in &#x60;yyyy-mm-dd&#x60; format. For example, 2017-05-20. | [optional] 
**due_date** | **date** | The date by which the payment for the debit memo is due, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**id** | **str** | The unique ID of the debit memo. | [optional] 
**invoice_group_number** | **str** | The number of invoice group associated with the debit memo.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**latest_pdf_file_id** | **str** | The ID of the latest PDF file generated for the debit memo. | [optional] 
**number** | **str** | The unique identification number of the debit memo. | [optional] 
**payment_term** | **str** | The name of the payment term associated with the debit memo.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**posted_by_id** | **str** | The ID of the Zuora user who posted the debit memo. | [optional] 
**posted_on** | **str** | The date and time when the debit memo was posted, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. | [optional] 
**referred_credit_memo_id** | **str** | The ID of the credit memo from which the debit memo was created. | [optional] 
**referred_invoice_id** | **str** | The ID of a referred invoice. | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the debit memo.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**sold_to_contact_id** | **str** | The ID of the sold-to contact associated with the debit memo.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**sold_to_contact_snapshot_id** | **str** | The ID of the sold-to contact snapshot associated with the debit memo.  The value of this field is &#x60;null&#x60; if you have the [Flexible Billing Attributes](https://knowledgecenter.zuora.com/Billing/Subscriptions/Flexible_Billing_Attributes) feature disabled. | [optional] 
**source_type** | [**MemoSourceType**](MemoSourceType.md) |  | [optional] 
**status** | [**BillingDocumentStatus**](BillingDocumentStatus.md) |  | [optional] 
**target_date** | **date** | The target date for the debit memo, in &#x60;yyyy-mm-dd&#x60; format. For example, 2017-07-20. | [optional] 
**tax_amount** | **float** | The amount of taxation. | [optional] 
**tax_message** | **str** | The message about the status of tax calculation related to the debit memo. If tax calculation fails in one debit memo, this field displays the reason for the failure. | [optional] 
**tax_status** | [**TaxStatus**](TaxStatus.md) |  | [optional] 
**total_tax_exempt_amount** | **float** | The calculated tax amount excluded due to the exemption. | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the debit memo. | [optional] 
**updated_date** | **str** | The date and time when the debit memo was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:31:10. | [optional] 
**e_invoice_status** | [**EInvoiceStatus**](EInvoiceStatus.md) |  | [optional] 
**e_invoice_error_code** | **str** | eInvoiceErrorCode.  | [optional] 
**e_invoice_error_message** | **str** | eInvoiceErrorMessage.  | [optional] 
**e_invoice_file_id** | **str** | eInvoiceFileId.  | [optional] 
**bill_to_contact_snapshot_id** | **str** | billToContactSnapshotId.  | [optional] 
**organization_label** | **str** | organization label.  | [optional] 
**currency** | **str** | Currency code. | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile associated with the debit memo. | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the debit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the debit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_response import DebitMemoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoResponse from a JSON string
debit_memo_response_instance = DebitMemoResponse.from_json(json)
# print the JSON string representation of the object
print(DebitMemoResponse.to_json())

# convert the object into a dict
debit_memo_response_dict = debit_memo_response_instance.to_dict()
# create an instance of DebitMemoResponse from a dict
debit_memo_response_from_dict = DebitMemoResponse.from_dict(debit_memo_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


