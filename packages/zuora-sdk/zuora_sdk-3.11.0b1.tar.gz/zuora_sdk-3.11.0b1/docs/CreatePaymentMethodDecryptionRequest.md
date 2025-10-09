# CreatePaymentMethodDecryptionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account associated with this payment method. To create an orphan payment method that is not associated with any customer account, you do not need to specify this field during creation. However, you must associate the orphan payment method with a customer account within 10 days. Otherwise, this orphan payment method will be deleted. | [optional] 
**card_holder_info** | [**CreatePaymentMethodCardholderInfo**](CreatePaymentMethodCardholderInfo.md) |  | [optional] 
**integration_type** | **str** | Field to identify the token decryption type.  **Note:** The only value at this time is &#x60;ApplePay&#x60;.   | 
**invoice_id** | **str** | The id of invoice this payment will apply to.  **Note:** When &#x60;processPayment&#x60; is &#x60;true&#x60;, this field is required. Only one invoice can be paid; for scenarios where you want to pay for multiple invoices, set &#x60;processPayment&#x60; to &#x60;false&#x60; and call payment API separately.  | [optional] 
**merchant_id** | **str** | The Merchant ID that was configured for use with Apple Pay in the Apple iOS Developer Center.  | 
**mit_consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | [optional] 
**mit_profile_action** | [**StoredCredentialProfileAction**](StoredCredentialProfileAction.md) |  | [optional] 
**mit_profile_type** | [**StoredCredentialProfileType**](StoredCredentialProfileType.md) |  | [optional] 
**payment_gateway** | **str** | The label name of the gateway instance configured in Zuora that should process the payment. When creating a Payment, this must be a valid gateway instance ID and this gateway must support the specific payment method. If not specified, the default gateway of your Zuora customer account will be used.  **Note:** When &#x60;processPayment&#x60; is &#x60;true&#x60;, this field is required. When &#x60;processPayment&#x60; is &#x60;false&#x60;, the default payment gateway of your Zuora customer account will be used no matter whether a payment gateway instance is specified in the &#x60;paymentGateway&#x60; field.  | [optional] 
**payment_token** | **object** | The complete JSON Object representing the encrypted payment token payload returned in the response from the Apple Pay session.   | 
**process_payment** | **bool** | A boolean flag to control whether a payment should be processed after creating payment method. The payment amount will be equivalent to the amount the merchant supplied in the ApplePay session. Default is false.  If this field is set to &#x60;true&#x60;, you must specify the &#x60;paymentGateway&#x60; field with the payment gateway instance name.  If this field is set to &#x60;false&#x60;:  - The default payment gateway of your Zuora customer account will be used no matter whether a payment gateway instance is specified in the &#x60;paymentGateway&#x60; field.    - You must select the **Verify new credit card** check box on the gateway instance settings page. Otherwise, the cryptogram will not be sent to the gateway.   - A separate subscribe or payment API call is required after this payment method creation call.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_decryption_request import CreatePaymentMethodDecryptionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodDecryptionRequest from a JSON string
create_payment_method_decryption_request_instance = CreatePaymentMethodDecryptionRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodDecryptionRequest.to_json())

# convert the object into a dict
create_payment_method_decryption_request_dict = create_payment_method_decryption_request_instance.to_dict()
# create an instance of CreatePaymentMethodDecryptionRequest from a dict
create_payment_method_decryption_request_from_dict = CreatePaymentMethodDecryptionRequest.from_dict(create_payment_method_decryption_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


