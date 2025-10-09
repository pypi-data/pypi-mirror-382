# CreatePaymentMethodCCReferenceTransaction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_card_mask_number** | **str** | The masked credit card number, such as:  &#x60;&#x60;&#x60;  *********1112  &#x60;&#x60;&#x60;   This field is specific for the CC Reference Transaction payment method. It is an optional field that you can use to distinguish different CC Reference Transaction payment methods.   Though there are no special restrictions on the input string, it is highly recommended to specify a card number that is masked. | [optional] 
**second_token_id** | **str** | A gateway unique identifier that replaces sensitive payment method data.  &#x60;secondTokenId&#x60; is conditionally required only when &#x60;tokenId&#x60; is being used to represent a gateway customer profile. &#x60;secondTokenId&#x60; is used in the CC Reference Transaction payment method.  | [optional] 
**token_id** | **str** | A gateway unique identifier that replaces sensitive payment method data or represents a gateway&#39;s unique customer profile. &#x60;tokenId&#x60; is required for the CC Reference Transaction payment method.   When &#x60;tokenId&#x60; is used to represent a customer profile, &#x60;secondTokenId&#x60; is conditionally required for representing the underlying tokenized payment method.   The values for the &#x60;tokenId&#x60; and &#x60;secondTokenId&#x60; fields differ for gateways. For more information, see the Knowledge Center article specific to each gateway that supports the CC Reference Transaction payment method.   **Note:** When creating an ACH payment method, if you need to pass in tokenized information, use the &#x60;mandateId&#x60; instead of &#x60;tokenId&#x60; field. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_cc_reference_transaction import CreatePaymentMethodCCReferenceTransaction

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodCCReferenceTransaction from a JSON string
create_payment_method_cc_reference_transaction_instance = CreatePaymentMethodCCReferenceTransaction.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodCCReferenceTransaction.to_json())

# convert the object into a dict
create_payment_method_cc_reference_transaction_dict = create_payment_method_cc_reference_transaction_instance.to_dict()
# create an instance of CreatePaymentMethodCCReferenceTransaction from a dict
create_payment_method_cc_reference_transaction_from_dict = CreatePaymentMethodCCReferenceTransaction.from_dict(create_payment_method_cc_reference_transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


