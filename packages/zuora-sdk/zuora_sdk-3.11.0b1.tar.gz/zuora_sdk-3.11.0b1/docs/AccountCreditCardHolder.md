# AccountCreditCardHolder

Information about the cardholder of a credit card payment method associated with an account. If you do not provide information about the cardholder, Zuora uses the account's bill-to contact.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_line1** | **str** | First line of the cardholder&#39;s address.  | [optional] 
**address_line2** | **str** | Second line of the cardholder&#39;s address.  | [optional] 
**card_holder_name** | **str** | Full name of the cardholder as it appears on the card. For example, \&quot;John J Smith\&quot;. | [optional] 
**city** | **str** | City of the cardholder&#39;s address.   It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | [optional] 
**country** | **str** | Country of the cardholder&#39;s address. The value of this field must be a valid country name or abbreviation.   It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | [optional] 
**email** | **str** | Email address of the cardholder.  | [optional] 
**phone** | **str** | Phone number of the cardholder.  | [optional] 
**state** | **str** | State or province of the cardholder&#39;s address.  | [optional] 
**zip_code** | **str** | ZIP code or other postal code of the cardholder&#39;s address.  | [optional] 

## Example

```python
from zuora_sdk.models.account_credit_card_holder import AccountCreditCardHolder

# TODO update the JSON string below
json = "{}"
# create an instance of AccountCreditCardHolder from a JSON string
account_credit_card_holder_instance = AccountCreditCardHolder.from_json(json)
# print the JSON string representation of the object
print(AccountCreditCardHolder.to_json())

# convert the object into a dict
account_credit_card_holder_dict = account_credit_card_holder_instance.to_dict()
# create an instance of AccountCreditCardHolder from a dict
account_credit_card_holder_from_dict = AccountCreditCardHolder.from_dict(account_credit_card_holder_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


