# RefundCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the refund&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the refund was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**syncto_net_suite__ns** | **str** | Specifies whether the refund should be synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**comment** | **str** | Comments about the refund. | [optional] 
**custom_rates** | [**List[CustomRates]**](CustomRates.md) | It contains Home currency and Reporting currency custom rates currencies. The maximum number of items is 2 (you can pass the Home currency item, Reporting currency item, or both).  **Note**: The API custom rate feature is permission controlled. | [optional] 
**finance_information** | [**CreateNonRefRefundFinanceInformation**](CreateNonRefRefundFinanceInformation.md) |  | [optional] 
**gateway_id** | **str** | The ID of the gateway instance that processes the refund. This field can be specified only for electronic refunds. The ID must be a valid gateway instance ID, and this gateway must support the specific payment method.   If no gateway ID is specified, the default gateway in the billing account configuration will be used. If no gateway is specified in the billing account, the default gateway of the corresponding tenant will be used.  | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**items** | [**List[RefundCreditMemoItemRequest]**](RefundCreditMemoItemRequest.md) | Container for credit memo items. The maximum number of items is 1,000.  **Note:** This field is only available if you have the [Invoice Item Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/C_Invoice_Item_Settlement) feature enabled. Invoice Item Settlement must be used together with other Invoice Settlement features (Unapplied Payments, and Credit and Debit memos).  If you wish to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 
**method_type** | [**PaymentMethodType**](PaymentMethodType.md) |  | [optional] 
**payment_method_id** | **str** | The ID of the payment method used for the refund. This field is required for an electronic refund, and the value must be an electronic payment method ID. This field must be left empty for an external refund.   | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code. | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway for an electronic refund. Use this field to reconcile refunds between your gateway and Zuora Payments. | [optional] 
**refund_date** | **date** | The date when the refund takes effect, in &#x60;yyyy-mm-dd&#x60; format. The date of the refund cannot be before the credit memo date. Specify this field only for external refunds. Zuora automatically generates this field for electronic refunds. | [optional] 
**second_refund_reference_id** | **str** | The transaction ID returned by the payment gateway if there is an additional transaction for the refund. Use this field to reconcile payments between your gateway and Zuora Payments. | [optional] 
**soft_descriptor** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**soft_descriptor_phone** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**total_amount** | **float** | The total amount of the refund. The amount cannot exceed the unapplied amount of the associated credit memo. If the original credit memo was applied to one or more invoices or debit memos, you have to unapply a full or partial credit memo from the invoices or debit memos, and then refund the full or partial unapplied credit memo to your customers. | 
**type** | **str** | The type of the refund. | 

## Example

```python
from zuora_sdk.models.refund_credit_memo_request import RefundCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RefundCreditMemoRequest from a JSON string
refund_credit_memo_request_instance = RefundCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(RefundCreditMemoRequest.to_json())

# convert the object into a dict
refund_credit_memo_request_dict = refund_credit_memo_request_instance.to_dict()
# create an instance of RefundCreditMemoRequest from a dict
refund_credit_memo_request_from_dict = RefundCreditMemoRequest.from_dict(refund_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


