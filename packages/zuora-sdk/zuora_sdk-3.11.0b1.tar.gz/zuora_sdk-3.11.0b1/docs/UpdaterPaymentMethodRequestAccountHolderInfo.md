# UpdaterPaymentMethodRequestAccountHolderInfo

The account holder information. This field is not supported in updating Credit Card Reference Transaction payment methods.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_line1** | **str** | The first line of the address for the account holder.   This field is required for SEPA Direct Debit payment methods on Stripe v2 for [certain countries](https://stripe.com/docs/payments/sepa-debit/set-up-payment?platform&#x3D;web#web-submit-payment-method). | [optional] 
**address_line2** | **str** | The second line of the address for the account holder.   | [optional] 
**city** | **str** | The city where the account holder stays.  | [optional] 
**country** | **str** | The country where the account holder stays.   This field is required for SEPA payment methods on Stripe v2 for [certain countries](https://stripe.com/docs/payments/sepa-debit/set-up-payment?platform&#x3D;web#web-submit-payment-method). | [optional] 
**email** | **str** | The email address of the account holder.  | [optional] 
**phone** | **str** | The phone number of the account holder.  | [optional] 
**state** | **str** | The state where the account holder stays.  | [optional] 
**zip_code** | **str** | The zip code for the address of the account holder.  | [optional] 

## Example

```python
from zuora_sdk.models.updater_payment_method_request_account_holder_info import UpdaterPaymentMethodRequestAccountHolderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of UpdaterPaymentMethodRequestAccountHolderInfo from a JSON string
updater_payment_method_request_account_holder_info_instance = UpdaterPaymentMethodRequestAccountHolderInfo.from_json(json)
# print the JSON string representation of the object
print(UpdaterPaymentMethodRequestAccountHolderInfo.to_json())

# convert the object into a dict
updater_payment_method_request_account_holder_info_dict = updater_payment_method_request_account_holder_info_instance.to_dict()
# create an instance of UpdaterPaymentMethodRequestAccountHolderInfo from a dict
updater_payment_method_request_account_holder_info_from_dict = UpdaterPaymentMethodRequestAccountHolderInfo.from_dict(updater_payment_method_request_account_holder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


