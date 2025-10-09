# CreateAuthorizationRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the customer account. Either &#x60;accountId&#x60; or &#x60;accountNumber&#x60; is required. | [optional] 
**account_number** | **str** | The number of the customer account. Either &#x60;accountNumber&#x60; or &#x60;accountId&#x60; is required. | [optional] 
**amount** | **float** | The amount of the trasaction. | 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**gateway_order_id** | **str** | The order ID for the specific gateway.  The specified order ID will be used in transaction authorization. If you specify an empty value for this field, Zuora will generate an ID and you will have to associate this ID with your order ID by yourself if needed. It is recommended to specify an ID for this field.  | 
**mit_transaction_source** | [**MitTransactionSource**](MitTransactionSource.md) |  | [optional] 
**payment_gateway_id** | **str** | The ID of the payment gateway instance. | [optional] 
**soft_descriptor** | **str** | A text, rendered on a cardholder’s statement, describing a particular product or service purchased by the cardholder. | [optional] 
**soft_descriptor_phone** | **str** | The phone number that relates to the soft descriptor, usually the phone number of customer service. | [optional] 
**cryptogram** | **str** | Cryptogram value supplied by the token provider if DPAN or network scheme token is present  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 

## Example

```python
from zuora_sdk.models.create_authorization_request import CreateAuthorizationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAuthorizationRequest from a JSON string
create_authorization_request_instance = CreateAuthorizationRequest.from_json(json)
# print the JSON string representation of the object
print(CreateAuthorizationRequest.to_json())

# convert the object into a dict
create_authorization_request_dict = create_authorization_request_instance.to_dict()
# create an instance of CreateAuthorizationRequest from a dict
create_authorization_request_from_dict = CreateAuthorizationRequest.from_dict(create_authorization_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


