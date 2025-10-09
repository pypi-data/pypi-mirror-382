# UpdateBasePaymentMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_key** | **str** | The ID of the customer account associated with this payment method, such as &#x60;2x92c0f859b0480f0159d3a4a6ee5bb6&#x60;.   **Note:** You can use this field to associate an orphan payment method with a customer account. If a payment method is already associated with a customer account, you cannot change the associated payment method through this operation. You cannot remove the previous account ID and leave this field empty, either. | [optional] 
**auth_gateway** | **str** | Specifies the ID of the payment gateway that Zuora will use to authorize the payments that are made with the payment method.  This field is not supported in updating Credit Card Reference Transaction payment methods.  | [optional] 
**payment_gateway_number** | **str** | The natural key for the payment gateway. | [optional] 
**currency_code** | **str** | The currency used for payment method authorization.  | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**use_default_retry_rule** | **bool** | Specifies whether to apply the default retry rule configured for your tenant in the Zuora Payments settings:   - To use the default retry rule, specify &#x60;true&#x60;.    - To use the custom retry rule specific to this payment method, specify &#x60;false&#x60;.  | [optional] 
**payment_retry_window** | **int** | The retry interval setting, which prevents making a payment attempt if the last failed attempt was within the last specified number of hours.  | [optional] 
**max_consecutive_payment_failures** | **int** | An optional client parameter that can be used for validating client-side HPM parameters.  See [Client parameters for Payment Pages 2.0](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/LA_Hosted_Payment_Pages/B_Payment_Pages_2.0/J_Client_Parameters_for_Payment_Pages_2.0) and [Validate client-side HPM parameters](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/LA_Hosted_Payment_Pages/B_Payment_Pages_2.0/F_Generate_the_Digital_Signature_for_Payment_Pages_2.0#Validate_Client-side_HPM_Parameters) for details.  | [optional] 
**ip_address** | **str** | The IPv4 or IPv6 information of the user when the payment method is created or updated. Some gateways use this field for fraud prevention.  If this field is passed to Zuora, Zuora directly passes it to gateways.  If the IP address length is beyond 45 characters, a validation error occurs. For validating SEPA payment methods on Stripe v2, this field is required.  | [optional] 
**processing_options** | [**PaymentMethodRequestProcessingOptions**](PaymentMethodRequestProcessingOptions.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_base_payment_method import UpdateBasePaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateBasePaymentMethod from a JSON string
update_base_payment_method_instance = UpdateBasePaymentMethod.from_json(json)
# print the JSON string representation of the object
print(UpdateBasePaymentMethod.to_json())

# convert the object into a dict
update_base_payment_method_dict = update_base_payment_method_instance.to_dict()
# create an instance of UpdateBasePaymentMethod from a dict
update_base_payment_method_from_dict = UpdateBasePaymentMethod.from_dict(update_base_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


