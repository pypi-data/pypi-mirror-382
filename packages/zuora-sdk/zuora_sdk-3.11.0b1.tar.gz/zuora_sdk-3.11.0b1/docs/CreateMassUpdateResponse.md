# CreateMassUpdateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bulk_key** | **str** | String of 32 characters that identifies the mass action. The bulkKey is generated before the mass action is processed. You can use the bulkKey to Get the Mass Action Result. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_mass_update_response import CreateMassUpdateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateMassUpdateResponse from a JSON string
create_mass_update_response_instance = CreateMassUpdateResponse.from_json(json)
# print the JSON string representation of the object
print(CreateMassUpdateResponse.to_json())

# convert the object into a dict
create_mass_update_response_dict = create_mass_update_response_instance.to_dict()
# create an instance of CreateMassUpdateResponse from a dict
create_mass_update_response_from_dict = CreateMassUpdateResponse.from_dict(create_mass_update_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


