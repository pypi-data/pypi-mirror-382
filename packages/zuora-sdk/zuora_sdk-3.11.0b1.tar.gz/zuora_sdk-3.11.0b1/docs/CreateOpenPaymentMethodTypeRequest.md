# CreateOpenPaymentMethodTypeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_id** | **str** | If this custom payment method type is specific to one entity only, provide the entity ID in this field in UUID format, such as &#x60;123e4567-e89b-12d3-a456-426614174000&#x60;. If no entity UUID is provided, the custom payment method type is available to the global entity and all the sub entities in the tenant.   You can get the entity ID through the [Multi-entity: List entities](https://www.zuora.com/developer/api-references/older-api/operation/Get_Entities/) API operation or the **Manage Entity Profile** administration setting in the UI. To convert the format of the entity ID to UUID, separate the entity ID string in five groups with hyphens, in the form &#x60;&lt;8-characters&gt;-&lt;4-characters&gt;-&lt;4-characters&gt;-&lt;4-characters&gt;-&lt;12-characters&gt;&#x60; for a total of 36 characters.   Note: After the custom payment method type is created, you can only update this field to be empty. | [optional] 
**fields** | [**List[OpenPaymentMethodTypeRequestFields]**](OpenPaymentMethodTypeRequestFields.md) | An array containing field metadata of the custom payment method type.  Notes:   - All the following nested metadata must be provided in the request to define a field.    - At least one field must be defined in the fields array for a custom payment method type.    - Up to 20 fields can be defined in the fields array for a custom payment method type.  | 
**internal_name** | **str** | A string to identify the custom payment method type in the API name of the payment method type.   This field must be alphanumeric, starting with a capital letter, excluding JSON preserved characters such as  * \\ ’ ”. Additionally, &#39;_&#39; or &#39;-&#39; is not allowed.   This field must be unique in a tenant.   This field is used along with the &#x60;tenantId&#x60; field by the system to construct and generate the API name of the custom payment method type in the following way:   &#x60;&lt;internalName&gt;__c_&lt;tenantId&gt;&#x60;   For example, if &#x60;internalName&#x60; is &#x60;AmazonPay&#x60;, and &#x60;tenantId&#x60; is &#x60;12368&#x60;, the API name of the custom payment method type will be &#x60;AmazonPay__c_12368&#x60;.   This field cannot be updated after the creation of the custom payment method type. | 
**label** | **str** | The label that is used to refer to this type in the Zuora UI.   This value must be alphanumeric, excluding JSON preserved characters such as  * \\ ’ ”  | 
**method_reference_id_field** | **str** | The identification reference of the custom payment method.   This field should be mapped to a field name defined in the &#x60;fields&#x60; array for the purpose of being used as a filter in reporting tools such as Payment Method Data Source Exports and Data Query.   This field cannot be updated after the creation of the custom payment method type. | 
**sub_type_field** | **str** | The identification reference indicating the subtype of the custom payment method.   This field should be mapped to a field name defined in the &#x60;fields&#x60; array for the purpose of being used as a filter in reporting tools such as Data Source Exports and Data Query.   This field cannot be updated after the creation of the custom payment method type. | [optional] 
**tenant_id** | **str** | Zuora tenant ID. If multi-entity is enabled in your tenant, this is the ID of the parent tenant of all the sub entities.   This field cannot be updated after the creation of the custom payment method type. | 
**user_reference_id_field** | **str** | The identification reference of the user or customer account.   This field should be mapped to a field name defined in the &#x60;fields&#x60; array for the purpose of being used as a filter in reporting tools such as Data Source Exports and Data Query.   This field cannot be updated after the creation of the custom payment method type. | [optional] 

## Example

```python
from zuora_sdk.models.create_open_payment_method_type_request import CreateOpenPaymentMethodTypeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOpenPaymentMethodTypeRequest from a JSON string
create_open_payment_method_type_request_instance = CreateOpenPaymentMethodTypeRequest.from_json(json)
# print the JSON string representation of the object
print(CreateOpenPaymentMethodTypeRequest.to_json())

# convert the object into a dict
create_open_payment_method_type_request_dict = create_open_payment_method_type_request_instance.to_dict()
# create an instance of CreateOpenPaymentMethodTypeRequest from a dict
create_open_payment_method_type_request_from_dict = CreateOpenPaymentMethodTypeRequest.from_dict(create_open_payment_method_type_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


