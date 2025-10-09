# CreditCard

Default payment method associated with an account. Only credit card payment methods are supported. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**card_holder_info** | [**AccountCreditCardHolder**](AccountCreditCardHolder.md) |  | [optional] 
**card_number** | **str** | Card number. Once set, you cannot update or query the value of this field. The value of this field is only available in masked format. For example, XXXX-XXXX-XXXX-1234 (hyphens must not be used when you set the credit card number).  | [optional] 
**card_type** | [**CreditCardCardType**](CreditCardCardType.md) |  | [optional] 
**expiration_month** | **int** | Expiration date of the card.  | [optional] 
**expiration_year** | **int** | Expiration year of the card.  | [optional] 
**security_code** | **str** | CVV or CVV2 security code of the card. To ensure PCI compliance, Zuora does not store the value of this field.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_card import CreditCard

# TODO update the JSON string below
json = "{}"
# create an instance of CreditCard from a JSON string
credit_card_instance = CreditCard.from_json(json)
# print the JSON string representation of the object
print(CreditCard.to_json())

# convert the object into a dict
credit_card_dict = credit_card_instance.to_dict()
# create an instance of CreditCard from a dict
credit_card_from_dict = CreditCard.from_dict(credit_card_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


