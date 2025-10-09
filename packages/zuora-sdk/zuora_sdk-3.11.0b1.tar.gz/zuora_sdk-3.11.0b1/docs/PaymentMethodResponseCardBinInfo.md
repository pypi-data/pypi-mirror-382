# PaymentMethodResponseCardBinInfo

The BIN information of a card payment method.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**brand** | **str** | The card brand, such as Visa and MasterCard. | [optional] 
**card_class** | [**PaymentMethodCardBinInfoCardClass**](PaymentMethodCardBinInfoCardClass.md) |  | [optional] 
**product_type** | [**PaymentMethodCardBinInfoProductType**](PaymentMethodCardBinInfoProductType.md) |  | [optional] 
**issuer** | **str** | The issuer bank of the card, such as JPMORGAN CHASE BANK N.A. | [optional] 
**issuing_country_code** | **str** | The issuing country code of the card, such as US. | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_card_bin_info import PaymentMethodResponseCardBinInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponseCardBinInfo from a JSON string
payment_method_response_card_bin_info_instance = PaymentMethodResponseCardBinInfo.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponseCardBinInfo.to_json())

# convert the object into a dict
payment_method_response_card_bin_info_dict = payment_method_response_card_bin_info_instance.to_dict()
# create an instance of PaymentMethodResponseCardBinInfo from a dict
payment_method_response_card_bin_info_from_dict = PaymentMethodResponseCardBinInfo.from_dict(payment_method_response_card_bin_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


