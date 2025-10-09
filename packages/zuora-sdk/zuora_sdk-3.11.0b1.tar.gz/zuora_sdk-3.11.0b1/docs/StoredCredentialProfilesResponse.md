# StoredCredentialProfilesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profiles** | [**List[StoredCredentialProfileResponse]**](StoredCredentialProfileResponse.md) | Container for stored credential profiles.  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.stored_credential_profiles_response import StoredCredentialProfilesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StoredCredentialProfilesResponse from a JSON string
stored_credential_profiles_response_instance = StoredCredentialProfilesResponse.from_json(json)
# print the JSON string representation of the object
print(StoredCredentialProfilesResponse.to_json())

# convert the object into a dict
stored_credential_profiles_response_dict = stored_credential_profiles_response_instance.to_dict()
# create an instance of StoredCredentialProfilesResponse from a dict
stored_credential_profiles_response_from_dict = StoredCredentialProfilesResponse.from_dict(stored_credential_profiles_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


