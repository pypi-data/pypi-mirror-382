# PaymentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account that the payment is for.  | [optional] 
**account_number** | **str** | The number of the customer account that the payment is for.  | [optional] 
**amount** | **float** | The total amount of the payment.  | [optional] 
**applied_amount** | **float** | The applied amount of the payment.  | [optional] 
**auth_transaction_id** | **str** | The authorization transaction ID from the payment gateway.  | [optional] 
**bank_identification_number** | **str** | The first six or eight digits of the credit card or debit card used for the payment, when applicable.  | [optional] 
**cancelled_on** | **str** | The date and time when the payment was cancelled, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**comment** | **str** | Comments about the payment.  | [optional] 
**created_by_id** | **str** | The ID of the Zuora user who created the payment.  | [optional] 
**created_date** | **str** | The date and time when the payment was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-01 15:31:10.  | [optional] 
**credit_balance_amount** | **float** | The amount that the payment transfers to the credit balance. The value is not &#x60;0&#x60; only for those payments that come from legacy payment operations performed without the Invoice Settlement feature.  | [optional] 
**currency** | **str** | When Standalone Payment is not enabled, the &#x60;currency&#x60; of the payment must be the same as the payment currency defined in the customer account settings through Zuora UI.  When Standalone Payment is enabled and &#x60;standalone&#x60; is &#x60;true&#x60;, the &#x60;currency&#x60; of the standalone payment can be different from the payment currency defined in the customer account settings. The amount will not be summed up to the account balance or key metrics regardless of currency.  | [optional] 
**effective_date** | **str** | The date and time when the payment takes effect, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**finance_information** | [**GetPaymentFinanceInformation**](GetPaymentFinanceInformation.md) |  | [optional] 
**gateway_id** | **str** | The ID of the gateway instance that processes the payment.  | [optional] 
**gateway_order_id** | **str** | A merchant-specified natural key value that can be passed to the electronic payment gateway when a payment is created.  If not specified, the payment number will be passed in instead.  | [optional] 
**gateway_reconciliation_reason** | **str** | The reason of gateway reconciliation.  | [optional] 
**gateway_reconciliation_status** | **str** | The status of gateway reconciliation.  | [optional] 
**gateway_response** | **str** | The message returned from the payment gateway for the payment. This message is gateway-dependent.  | [optional] 
**gateway_response_code** | **str** | The code returned from the payment gateway for the payment. This code is gateway-dependent.  | [optional] 
**gateway_state** | [**GatewayState**](GatewayState.md) |  | [optional] 
**id** | **str** | The unique ID of the created payment. For example, 4028905f5a87c0ff015a87eb6b75007f.  | [optional] 
**marked_for_submission_on** | **str** | The date and time when a payment was marked and waiting for batch submission to the payment process, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**number** | **str** | The unique identification number of the payment. For example, P-00000001.  | [optional] 
**payment_method_id** | **str** | The unique ID of the payment method that the customer used to make the payment.  | [optional] 
**payment_method_snapshot_id** | **str** | The unique ID of the payment method snapshot which is a copy of the particular Payment Method used in a transaction.  | [optional] 
**payment_option** | [**List[PaymentSchedulePaymentOptionFields]**](PaymentSchedulePaymentOptionFields.md) | Container for the paymentOption items, which describe the transactional level rules for processing payments. Currently, only the Gateway Options type is supported.  &#x60;paymentOption&#x60; of the payment schedule takes precedence over &#x60;paymentOption&#x60; of the payment schedule item.  This field is only available if &#x60;zuora-version&#x60; is set to 337.0 or later.  | [optional] 
**payment_schedule_key** | **str** | The unique ID or the number of the payment schedule that is linked to the payment. See [Link payments to payment schedules](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Payment_Schedules/Link_payments_with_payment_schedules) for more information. | [optional] 
**payout_id** | **str** | The payout ID of the payment from the gateway side.  | [optional] 
**prepayment** | **bool** | Indicates whether the payment is used as a reserved payment. See [Prepaid Cash with Drawdown](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Invoicing/JA_Advanced_Consumption_Billing/Prepaid_Cash_with_Drawdown) for more information.  | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway. Use this field to reconcile payments between your gateway and Zuora Payments.  | [optional] 
**refund_amount** | **float** | The amount of the payment that is refunded.  | [optional] 
**second_payment_reference_id** | **str** | The transaction ID returned by the payment gateway if there is an additional transaction for the payment. Use this field to reconcile payments between your gateway and Zuora Payments.  | [optional] 
**settled_on** | **str** | The date and time when the payment was settled in the payment processor, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. This field is used by the Spectrum gateway only and not applicable to other gateways.  | [optional] 
**soft_descriptor** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi.  | [optional] 
**soft_descriptor_phone** | **str** | A payment gateway-specific field that maps to Zuora for the gateways, Orbital, Vantiv and Verifi.  | [optional] 
**standalone** | **bool** | This field is only available if the support for standalone payment is enabled. This field is not available for transferring, applying, or unapplying a payment.  The value &#x60;true&#x60; indicates this is a standalone payment that is created and processed in Zuora through Zuora gateway integration but will be settled outside of Zuora. No settlement data will be created. The standalone payment cannot be applied, unapplied, or transferred.  The value &#x60;false&#x60; indicates this is an ordinary payment that is created, processed, and settled in Zuora.  | [optional] [default to False]
**status** | [**PaymentStatus**](PaymentStatus.md) |  | [optional] 
**submitted_on** | **str** | The date and time when the payment was submitted, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**type** | [**PaymentType**](PaymentType.md) |  | [optional] 
**unapplied_amount** | **float** | The unapplied amount of the payment.  | [optional] 
**updated_by_id** | **str** | The ID of the Zuora user who last updated the payment.  | [optional] 
**updated_date** | **str** | The date and time when the payment was last updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format. For example, 2017-03-02 15:36:10.  | [optional] 
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.payment_response import PaymentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentResponse from a JSON string
payment_response_instance = PaymentResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentResponse.to_json())

# convert the object into a dict
payment_response_dict = payment_response_instance.to_dict()
# create an instance of PaymentResponse from a dict
payment_response_from_dict = PaymentResponse.from_dict(payment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


