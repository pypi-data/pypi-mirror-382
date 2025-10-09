# DocumentIdList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**doc_type** | [**BillingDocumentType**](BillingDocumentType.md) |  | [optional] 
**object_ids** | **List[str]** | Collection of Billing Document Ids | [optional] 

## Example

```python
from zuora_sdk.models.document_id_list import DocumentIdList

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentIdList from a JSON string
document_id_list_instance = DocumentIdList.from_json(json)
# print the JSON string representation of the object
print(DocumentIdList.to_json())

# convert the object into a dict
document_id_list_dict = document_id_list_instance.to_dict()
# create an instance of DocumentIdList from a dict
document_id_list_from_dict = DocumentIdList.from_dict(document_id_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


