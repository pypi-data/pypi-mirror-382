# PostCustomObjectDefinitionsRequestDefinition


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auditable** | **List[str]** | The set of fields which Audit Trail tracks and records changes of. You can change auditable fields to non-auditable, and vice versa. One custom object can have a maximum of five auditable fields. | [optional] 
**enable_create_record_auditing** | **bool** | Indicates whether to audit the creation of custom object records of this custom object definition.   Note that you must enable the **Custom Object Definition** audit trail setting in your Zuora tenant before auditing custom object record creation. For more information, see &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/Tenant_Management/A_Administrator_Settings/Manage_Audit_Trail_Settings\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Manage audit trail settings&lt;/a&gt;. | [optional] [default to False]
**enable_delete_record_auditing** | **bool** | Indicates whether to audit the deletion of custom object records of this custom object definition.   Note that you must enable the **Custom Object Definition** audit trail setting in your Zuora tenant before auditing custom object record deletion. For more information, see &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Central_Platform/Tenant_Management/A_Administrator_Settings/Manage_Audit_Trail_Settings\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Manage audit trail settings&lt;/a&gt;. | [optional] [default to False]
**filterable** | **List[str]** | The set of fields that are allowed to be queried on. Queries on non-filterable fields will be rejected. You can not change a non-filterable field to filterable. | [optional] 
**label** | **str** | A UI label for the custom object | 
**object** | **str** | The API name of the custom object | 
**properties** | [**Dict[str, PostCustomObjectDefinitionFieldDefinitionRequest]**](PostCustomObjectDefinitionFieldDefinitionRequest.md) |  | [optional] 
**relationships** | [**List[CustomObjectDefinitionRelationship]**](CustomObjectDefinitionRelationship.md) | An array of relationships with Zuora objects or other custom objects. You can add at most 2 &#x60;manyToOne&#x60; relationships when creating a custom field definition. | [optional] 
**required** | **List[str]** | The required fields of the custom object. You can change required fields to optional. However, you can only change optional fields to required on the custom objects with no records. | [optional] 
**unique** | **List[str]** | The fields with unique constraints. You can remove the unique constraint on a field. However, you can only add a unique constraint to a filterable field if the custom object contains no record. One custom object can have a maximum of five fields with unique constraints. | [optional] 

## Example

```python
from zuora_sdk.models.post_custom_object_definitions_request_definition import PostCustomObjectDefinitionsRequestDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of PostCustomObjectDefinitionsRequestDefinition from a JSON string
post_custom_object_definitions_request_definition_instance = PostCustomObjectDefinitionsRequestDefinition.from_json(json)
# print the JSON string representation of the object
print(PostCustomObjectDefinitionsRequestDefinition.to_json())

# convert the object into a dict
post_custom_object_definitions_request_definition_dict = post_custom_object_definitions_request_definition_instance.to_dict()
# create an instance of PostCustomObjectDefinitionsRequestDefinition from a dict
post_custom_object_definitions_request_definition_from_dict = PostCustomObjectDefinitionsRequestDefinition.from_dict(post_custom_object_definitions_request_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


