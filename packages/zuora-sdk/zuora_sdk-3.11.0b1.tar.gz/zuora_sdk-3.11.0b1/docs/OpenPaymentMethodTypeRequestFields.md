# OpenPaymentMethodTypeRequestFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**checksum** | **bool** | The checksum value of a payment method is used to identify if this payment method is the same as another one, or if this payment method is altered to another new payment method.  Set this flag to &#x60;true&#x60; for the following scenarios:   - The field should be part of checksum calculation.   - The field is a critical differentiator for this type.       For example, if you select the credit card number and expiration date as the checksum fields for the CreditCard payment method type, when you modified the expiration date, Zuora considers this payment method as a different payment method compared to the original one.  This field cannot be &#x60;null&#x60; or empty.  This field cannot be updated after the creation of the custom payment method type.  | [optional] 
**default_value** | **str** | The default value of the field. &#x60;null&#x60; is supported.  If a required field is added after the custom payment method type is published, &#x60;defaultValue&#x60; is required.  This field cannot be updated after the creation of the custom payment method type.  | [optional] 
**description** | **str** | An explanation of this field. It can be an empty string.  | [optional] 
**editable** | **bool** | Specify &#x60;true&#x60; if this field can be updated through PUT API or UI.  This field cannot be &#x60;null&#x60; or empty.  Note: If &#x60;editable&#x60; is set to &#x60;false&#x60;, you can specify the value of this field in the UI and POST API when creating a payment method. However, after you created the payment method, you cannot edit this field through PUT API or UI.  | [optional] 
**index** | **int** | The order of the field in this type, starting from 1. It must be unique.  This field cannot be &#x60;null&#x60; or empty.  This field cannot be updated after the creation of the custom payment method type.  | [optional] 
**label** | **str** | The label that is used to refer to this field in the Zuora UI.  nAn alphanumeric string, excluding JSON preserved characters e.g.  * \\ ’ ”  This field cannot be &#x60;null&#x60; or empty or any reserved field name.  | [optional] 
**max_length** | **int** | A maximum length limitation of the field value. The specified value must be in the range of [1,8000]. &#x60;maxLength&#x60; must be greater than or equal to &#x60;minLength&#x60;.  After the custom payment method type is created, you can only increase the value of &#x60;maxLength&#x60;. Decreasing the value is not supported.  | [optional] 
**min_length** | **int** | A minimal length limitation of the field value.      0 &lt;&#x3D; &#x60;minLength&#x60; &lt;&#x3D; &#x60;maxLength&#x60;  The value of this metadata does not determine whether the field is a required field. It only defines the minimal length of the field value.  After the custom payment method type is created, you can only decrease the value of &#x60;minLength&#x60;. Increasing the value is not supported.  | [optional] 
**name** | **str** | The API name of this field. It must be uinique.  An alphanumeric string starting with a capital letter, excluding JSON preserved characters e.g.  * \\ ’ ”  Though this field must be defined with a string starting with a capital letter, use this string with the first letter in lowercase when you specify it in other API operations. For example, &#x60;AmazonPayToken&#x60; is the defined value for &#x60;name&#x60;. In the request of the \&quot;Create a payment method\&quot; API operation, use &#x60;amazonPayToken&#x60;.  This field cannot be &#x60;null&#x60; or empty or any reserved field name.  This field cannot be updated after the creation of the custom payment method type.  | [optional] 
**representer** | **bool** | This flag determines whether this field will be used for identifying this payment method in the Zuora UI. The field will be shown in the Payment Method field in the UI.  This field cannot be &#x60;null&#x60; or empty.  Notes:  - In one custom payment method type, set &#x60;representer&#x60; to &#x60;true&#x60; for at least one field .   - In one custom payment method type, you can set &#x60;representer&#x60; to &#x60;true&#x60; for multiple fields.  | [optional] 
**required** | **bool** | Specify whether this field is required.  This field cannot be &#x60;null&#x60; or empty.  This field cannot be updated after the creation of the custom payment method type.  | [optional] 
**type** | [**OpenPaymentMethodTypeFieldsType**](OpenPaymentMethodTypeFieldsType.md) |  | [optional] 
**visible** | **bool** | Specify &#x60;true&#x60; if this field can be retrieved through GET API or UI for displaying payment method details.  This field cannot be &#x60;null&#x60; or empty.  Notes:    - If &#x60;visible&#x60; is set to &#x60;false&#x60;, you can still specify the value of this field in the UI and POST API when creating the payment method.  - If &#x60;visible&#x60; is set to &#x60;false&#x60; and &#x60;editable&#x60; is set to &#x60;true&#x60;, this field is not accessible through GET API or UI for displaying details, but you can still see it and edit the value in the UI and PUT API when updating this payment method.  | [optional] 

## Example

```python
from zuora_sdk.models.open_payment_method_type_request_fields import OpenPaymentMethodTypeRequestFields

# TODO update the JSON string below
json = "{}"
# create an instance of OpenPaymentMethodTypeRequestFields from a JSON string
open_payment_method_type_request_fields_instance = OpenPaymentMethodTypeRequestFields.from_json(json)
# print the JSON string representation of the object
print(OpenPaymentMethodTypeRequestFields.to_json())

# convert the object into a dict
open_payment_method_type_request_fields_dict = open_payment_method_type_request_fields_instance.to_dict()
# create an instance of OpenPaymentMethodTypeRequestFields from a dict
open_payment_method_type_request_fields_from_dict = OpenPaymentMethodTypeRequestFields.from_dict(open_payment_method_type_request_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


