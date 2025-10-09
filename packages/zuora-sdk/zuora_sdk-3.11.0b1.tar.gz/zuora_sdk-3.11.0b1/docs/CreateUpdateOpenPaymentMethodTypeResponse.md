# CreateUpdateOpenPaymentMethodTypeResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_method_type** | **str** | The API name of the custom payment method type.  | [optional] 
**publish_date** | **str** | The date when the custom payment method type was published. It is empty if the custom payment method type has not been published yet. | [optional] 
**revision** | **int** | The revision number of the custom payment method type, which starts from 1 and increases by 1 when you update a published revision for the first time. | [optional] 
**status** | **str** | The status of the custom payment method type.  | [optional] 

## Example

```python
from zuora_sdk.models.create_update_open_payment_method_type_response import CreateUpdateOpenPaymentMethodTypeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUpdateOpenPaymentMethodTypeResponse from a JSON string
create_update_open_payment_method_type_response_instance = CreateUpdateOpenPaymentMethodTypeResponse.from_json(json)
# print the JSON string representation of the object
print(CreateUpdateOpenPaymentMethodTypeResponse.to_json())

# convert the object into a dict
create_update_open_payment_method_type_response_dict = create_update_open_payment_method_type_response_instance.to_dict()
# create an instance of CreateUpdateOpenPaymentMethodTypeResponse from a dict
create_update_open_payment_method_type_response_from_dict = CreateUpdateOpenPaymentMethodTypeResponse.from_dict(create_update_open_payment_method_type_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


