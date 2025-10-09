# Bi3ViewsColumnsDescriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**column_name** | **str** | The name of the column in the view. | [optional] 
**data_type** | **str** | The data type of the column (e.g., VARCHAR, INTEGER). | [optional] 
**nullable** | **bool** | Whether the column allows NULL values. | [optional] 
**description** | **str** | Additional details about the column. | [optional] 

## Example

```python
from zuora_sdk.models.bi3_views_columns_description_response import Bi3ViewsColumnsDescriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of Bi3ViewsColumnsDescriptionResponse from a JSON string
bi3_views_columns_description_response_instance = Bi3ViewsColumnsDescriptionResponse.from_json(json)
# print the JSON string representation of the object
print(Bi3ViewsColumnsDescriptionResponse.to_json())

# convert the object into a dict
bi3_views_columns_description_response_dict = bi3_views_columns_description_response_instance.to_dict()
# create an instance of Bi3ViewsColumnsDescriptionResponse from a dict
bi3_views_columns_description_response_from_dict = Bi3ViewsColumnsDescriptionResponse.from_dict(bi3_views_columns_description_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


