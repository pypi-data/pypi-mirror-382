# OmniChannelAccountData

The information of the account that you are to create when create Omni Channel Subscription.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_number** | **str** |  | [optional] 
**name** | **str** |  | 
**currency** | **str** | 3 uppercase character currency code.  | 
**notes** | **str** |  | [optional] 
**bill_to_contact** | [**ContactInfo**](ContactInfo.md) |  | 
**sold_to_contact** | [**ContactInfo**](ContactInfo.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields.  | [optional] 
**organization_label** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.omni_channel_account_data import OmniChannelAccountData

# TODO update the JSON string below
json = "{}"
# create an instance of OmniChannelAccountData from a JSON string
omni_channel_account_data_instance = OmniChannelAccountData.from_json(json)
# print the JSON string representation of the object
print(OmniChannelAccountData.to_json())

# convert the object into a dict
omni_channel_account_data_dict = omni_channel_account_data_instance.to_dict()
# create an instance of OmniChannelAccountData from a dict
omni_channel_account_data_from_dict = OmniChannelAccountData.from_dict(omni_channel_account_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


