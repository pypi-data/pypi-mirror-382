# RefundCreditMemoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the refund&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the refund was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**syncto_net_suite__ns** | **str** | Specifies whether the refund should be synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**account_id** | **str** | The ID of the account associated with this refund. Zuora associates the refund automatically with the account from the associated payment. | [optional] 
**amount** | **float** | The total amount of the refund. | [optional] 
**cancelled_on** | **str** | The date and time when the refund was cancelled, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**comment** | **str** | Comments about the refund. | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the refund. | [optional] 
**created_date** | **str** | The date and time when the refund was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-06 15:31:10. | [optional] 
**credit_memo_id** | **str** | The ID of the credit memo that is refunded. | [optional] 
**finance_information** | [**GetRefundCreditMemoFinanceInformation**](GetRefundCreditMemoFinanceInformation.md) |  | [optional] 
**gateway_id** | **str** | The ID of the gateway instance that processes the refund. | [optional] 
**gateway_response** | **str** | The message returned from the payment gateway for the refund. This message is gateway-dependent. | [optional] 
**gateway_response_code** | **str** | The response code returned from the payment gateway for the refund. This code is gateway-dependent. | [optional] 
**gateway_state** | [**GatewayState**](GatewayState.md) |  | [optional] 
**id** | **str** | The ID of the created refund. | [optional] 
**marked_for_submission_on** | **str** | The date and time when a refund was marked and waiting for batch submission to the payment process, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**method_type** | [**PaymentMethodType**](PaymentMethodType.md) |  | [optional] 
**number** | **str** | The unique identification number of the refund. | [optional] 
**payment_id** | **str** | The ID of the payment associated with the refund. | [optional] 
**payment_method_id** | **str** | The unique ID of the payment method that the customer used to make the refund. | [optional] 
**payment_method_snapshot_id** | **str** | The unique ID of the payment method snapshot, which is a copy of the particular payment method used in a transaction. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway for an electronic refund. Use this field to reconcile refunds between your gateway and Zuora Payments. | [optional] 
**refund_date** | **str** | The date when the refund takes effect, in yyyy-mm-dd format. | [optional] 
**refund_transaction_time** | **str** | The date and time when the refund was issued, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**second_refund_reference_id** | **str** | The transaction ID returned by the payment gateway if there is an additional transaction for the refund. Use this field to reconcile payments between your gateway and Zuora Payments. | [optional] 
**settled_on** | **datetime** | The date and time when the refund was settled in the payment processor, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. This field is used by the Spectrum gateway only and not applicable to other gateways. | [optional] 
**soft_descriptor** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**soft_descriptor_phone** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi. | [optional] 
**status** | **str** | The status of the refund. | [optional] 
**submitted_on** | **str** | The date and time when the refund was submitted, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 
**type** | **str** | The type of the refund. | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the refund. | [optional] 
**updated_date** | **str** | The date and time when the refund was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-07 15:36:10. | [optional] 

## Example

```python
from zuora_sdk.models.refund_credit_memo_response import RefundCreditMemoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RefundCreditMemoResponse from a JSON string
refund_credit_memo_response_instance = RefundCreditMemoResponse.from_json(json)
# print the JSON string representation of the object
print(RefundCreditMemoResponse.to_json())

# convert the object into a dict
refund_credit_memo_response_dict = refund_credit_memo_response_instance.to_dict()
# create an instance of RefundCreditMemoResponse from a dict
refund_credit_memo_response_from_dict = RefundCreditMemoResponse.from_dict(refund_credit_memo_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


