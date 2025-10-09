# RegenerateTransactionObjectResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 
**process_id** | **str** | The Id of the process that handles the operation.  | [optional] 
**id_list** | **List[str]** |  | [optional] 

## Example

```python
from zuora_sdk.models.regenerate_transaction_object_response import RegenerateTransactionObjectResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RegenerateTransactionObjectResponse from a JSON string
regenerate_transaction_object_response_instance = RegenerateTransactionObjectResponse.from_json(json)
# print the JSON string representation of the object
print(RegenerateTransactionObjectResponse.to_json())

# convert the object into a dict
regenerate_transaction_object_response_dict = regenerate_transaction_object_response_instance.to_dict()
# create an instance of RegenerateTransactionObjectResponse from a dict
regenerate_transaction_object_response_from_dict = RegenerateTransactionObjectResponse.from_dict(regenerate_transaction_object_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


