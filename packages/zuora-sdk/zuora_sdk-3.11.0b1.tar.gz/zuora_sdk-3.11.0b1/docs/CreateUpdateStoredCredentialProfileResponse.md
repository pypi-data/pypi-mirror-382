# CreateUpdateStoredCredentialProfileResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**number** | **int** | The number that identifies the stored credential profile within the payment method. | [optional] 
**payment_method_id** | **str** | ID of the payment method.  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.create_update_stored_credential_profile_response import CreateUpdateStoredCredentialProfileResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUpdateStoredCredentialProfileResponse from a JSON string
create_update_stored_credential_profile_response_instance = CreateUpdateStoredCredentialProfileResponse.from_json(json)
# print the JSON string representation of the object
print(CreateUpdateStoredCredentialProfileResponse.to_json())

# convert the object into a dict
create_update_stored_credential_profile_response_dict = create_update_stored_credential_profile_response_instance.to_dict()
# create an instance of CreateUpdateStoredCredentialProfileResponse from a dict
create_update_stored_credential_profile_response_from_dict = CreateUpdateStoredCredentialProfileResponse.from_dict(create_update_stored_credential_profile_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


