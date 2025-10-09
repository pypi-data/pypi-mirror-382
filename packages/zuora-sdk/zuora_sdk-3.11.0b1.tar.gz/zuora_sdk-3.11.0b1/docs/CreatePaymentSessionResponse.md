# CreatePaymentSessionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** | The token for the payment session data. Send the token back to your client side for identifying your website to Zuora.   For more information, see [Set up Apple Pay through the JavaScript SDK approach](https://knowledgecenter.zuora.com/Zuora_Payments/Payment_Methods/B_Define_Payment_Methods/Set_up_Apple_Pay_for_gateway_integrations_other_than_Adyen_Integration_v2.0). | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_session_response import CreatePaymentSessionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSessionResponse from a JSON string
create_payment_session_response_instance = CreatePaymentSessionResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSessionResponse.to_json())

# convert the object into a dict
create_payment_session_response_dict = create_payment_session_response_instance.to_dict()
# create an instance of CreatePaymentSessionResponse from a dict
create_payment_session_response_from_dict = CreatePaymentSessionResponse.from_dict(create_payment_session_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


