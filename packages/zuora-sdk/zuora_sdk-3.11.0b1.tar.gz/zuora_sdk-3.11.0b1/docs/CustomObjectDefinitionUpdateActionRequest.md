# CustomObjectDefinitionUpdateActionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Optional property for &#x60;updateObject&#x60; action | [optional] 
**enable_create_record_auditing** | **bool** | Optional property for &#x60;updateObject&#x60; action.  Indicates whether to audit the creation of custom object records of this custom object definition.  Note that you must enable the **Custom Object Definition** audit trail setting in your Zuora tenant before auditing custom object record creation. For more information, see &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/Tenant_Management/A_Administrator_Settings/Manage_Audit_Trail_Settings\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Manage audit trail settings&lt;/a&gt;.  | [optional] 
**enable_delete_record_auditing** | **bool** | Optional property for &#x60;updateObject&#x60; action.  Indicates whether to audit the deletion of custom object records of this custom object definition.  Note that you must enable the **Custom Object Definition** audit trail setting in your Zuora tenant before auditing custom object record deletion. For more information, see &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/Tenant_Management/A_Administrator_Settings/Manage_Audit_Trail_Settings\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Manage audit trail settings&lt;/a&gt;.  | [optional] 
**var_field** | [**UpdateCustomObjectCusotmField**](UpdateCustomObjectCusotmField.md) |  | [optional] 
**label** | **str** | Optional property for &#x60;updateObject&#x60; action | [optional] 
**namespace** | **str** | The namespace of the custom object definition to be updated | 
**object** | **str** | The API name of the custom object definition to be updated | 
**relationship** | **object** |  | [optional] 
**type** | [**CustomObjectDefinitionUpdateActionRequestType**](CustomObjectDefinitionUpdateActionRequestType.md) |  | 

## Example

```python
from zuora_sdk.models.custom_object_definition_update_action_request import CustomObjectDefinitionUpdateActionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectDefinitionUpdateActionRequest from a JSON string
custom_object_definition_update_action_request_instance = CustomObjectDefinitionUpdateActionRequest.from_json(json)
# print the JSON string representation of the object
print(CustomObjectDefinitionUpdateActionRequest.to_json())

# convert the object into a dict
custom_object_definition_update_action_request_dict = custom_object_definition_update_action_request_instance.to_dict()
# create an instance of CustomObjectDefinitionUpdateActionRequest from a dict
custom_object_definition_update_action_request_from_dict = CustomObjectDefinitionUpdateActionRequest.from_dict(custom_object_definition_update_action_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


