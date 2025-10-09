# CompareTemplateResponse

When Tenant's Compare API returns a result, this object is used to send the response to UI.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**custom_objects** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**data_access_control** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**meta_data** | **object** | Json node object contains metadata. | [optional] 
**notifications** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**product_catalog** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**settings** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 
**workflows** | [**List[CompareSchemaKeyValue]**](CompareSchemaKeyValue.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.compare_template_response import CompareTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CompareTemplateResponse from a JSON string
compare_template_response_instance = CompareTemplateResponse.from_json(json)
# print the JSON string representation of the object
print(CompareTemplateResponse.to_json())

# convert the object into a dict
compare_template_response_dict = compare_template_response_instance.to_dict()
# create an instance of CompareTemplateResponse from a dict
compare_template_response_from_dict = CompareTemplateResponse.from_dict(compare_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


