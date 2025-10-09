# UpdatePaymentRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**comment** | **str** | Comments about the payment.  | [optional] 
**finance_information** | [**PaymentRequestFinanceInformation**](PaymentRequestFinanceInformation.md) |  | [optional] 
**gateway_state** | **str** | This field is mainly used for gateway reconciliation. See &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Payments/Payment_Operations/DA_Electronic_Payment_Processing#Gateway_Reconciliation_Consideration\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Electronic payment processing&lt;/a&gt; for details.   You must have the **Edit Payment Gateway Status** &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/Tenant_Management/A_Administrator_Settings/User_Roles/e_Payments_Roles\&quot; target&#x3D;\&quot;_blank\&quot;&gt;user permission&lt;/a&gt; to update this field. | [optional] 
**payment_schedule_key** | **str** | The unique ID or the number of the payment schedule to be linked with the payment. See [Link payments to payment schedules](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Payment_Schedules/Link_payments_with_payment_schedules) for more information. | [optional] 
**reference_id** | **str** | The transaction ID returned by the payment gateway. Use this field to reconcile payments between your gateway and Zuora Payments.   You can only update the reference ID for external payments. | [optional] 
**gateway_reconciliation_status** | **str** |  | [optional] 
**gateway_reconciliation_reason** | **str** |  | [optional] 
**payout_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.update_payment_request import UpdatePaymentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePaymentRequest from a JSON string
update_payment_request_instance = UpdatePaymentRequest.from_json(json)
# print the JSON string representation of the object
print(UpdatePaymentRequest.to_json())

# convert the object into a dict
update_payment_request_dict = update_payment_request_instance.to_dict()
# create an instance of UpdatePaymentRequest from a dict
update_payment_request_from_dict = UpdatePaymentRequest.from_dict(update_payment_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


