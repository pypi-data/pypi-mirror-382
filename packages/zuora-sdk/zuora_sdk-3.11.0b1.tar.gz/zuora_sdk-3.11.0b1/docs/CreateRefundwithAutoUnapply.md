# CreateRefundwithAutoUnapply


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the refund.  | [optional] 
**debit_memos** | [**List[ApplyPaymentDebitMemoApplication]**](ApplyPaymentDebitMemoApplication.md) | Container for debit memos. The maximum number of debit memos is 1,000.  | [optional] 
**finance_information** | [**RefundRequestFinanceInformation**](RefundRequestFinanceInformation.md) |  | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**invoices** | [**List[ApplyPaymentInvoiceApplication]**](ApplyPaymentInvoiceApplication.md) | Container for invoices. The maximum number of invoices is 1,000.  | [optional] 
**method_type** | [**PaymentMethodType**](PaymentMethodType.md) |  | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code.  | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway for an electronic refund. Use this field to reconcile refunds between your gateway and Zuora Payments.  | [optional] 
**refund_date** | **date** | The date when the refund takes effect, in &#x60;yyyy-mm-dd&#x60; format. The date of the refund cannot be before the payment date. Specify this field only for external refunds. Zuora automatically generates this field for electronic refunds.  | [optional] 
**second_refund_reference_id** | **str** | The transaction ID returned by the payment gateway if there is an additional transaction for the refund. Use this field to reconcile payments between your gateway and Zuora Payments.  | [optional] 
**soft_descriptor** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**soft_descriptor_phone** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**total_amount** | **float** | The total amount of the refund.     - &#x60;Full Refund&#x60;: If the refund amount and debit memo/ invoice are not specified, then the payment will be unapplied completely, followed by processing a full refund.   - &#x60;Partial Refund&#x60;:        - If the total amount is specified, and the debit memo/invoice is not specified, you can unapply the refund amount from the available debit memo/invoice and refund the unapplied payment to the customer.  - If the total amount is specified, along with the debit memo and the invoice, you can unapply the applied payments from the mentioned invoices and debit memos, and refund the unapplied payments to customers.    | 
**type** | [**RefundType**](RefundType.md) |  | 
**refund_transaction_type** | [**RefundTransactionType**](RefundTransactionType.md) |  | [optional] 
**write_off** | **bool** | Indicates whether to write off a document. | [optional] [default to False]
**write_off_options** | [**WriteOffOptions**](WriteOffOptions.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_refundwith_auto_unapply import CreateRefundwithAutoUnapply

# TODO update the JSON string below
json = "{}"
# create an instance of CreateRefundwithAutoUnapply from a JSON string
create_refundwith_auto_unapply_instance = CreateRefundwithAutoUnapply.from_json(json)
# print the JSON string representation of the object
print(CreateRefundwithAutoUnapply.to_json())

# convert the object into a dict
create_refundwith_auto_unapply_dict = create_refundwith_auto_unapply_instance.to_dict()
# create an instance of CreateRefundwithAutoUnapply from a dict
create_refundwith_auto_unapply_from_dict = CreateRefundwithAutoUnapply.from_dict(create_refundwith_auto_unapply_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


