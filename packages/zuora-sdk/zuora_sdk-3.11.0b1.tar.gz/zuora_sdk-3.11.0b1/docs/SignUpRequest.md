# SignUpRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_data** | [**AccountData**](AccountData.md) |  | [optional] 
**account_identifier_field** | **str** | Specify the name of the field that holds external account id | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields.  | [optional] 
**options** | [**Options**](Options.md) |  | [optional] 
**payment_data** | [**PaymentData**](PaymentData.md) |  | [optional] 
**subscription_data** | [**SubscriptionData**](SubscriptionData.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.sign_up_request import SignUpRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpRequest from a JSON string
sign_up_request_instance = SignUpRequest.from_json(json)
# print the JSON string representation of the object
print(SignUpRequest.to_json())

# convert the object into a dict
sign_up_request_dict = sign_up_request_instance.to_dict()
# create an instance of SignUpRequest from a dict
sign_up_request_from_dict = SignUpRequest.from_dict(sign_up_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


