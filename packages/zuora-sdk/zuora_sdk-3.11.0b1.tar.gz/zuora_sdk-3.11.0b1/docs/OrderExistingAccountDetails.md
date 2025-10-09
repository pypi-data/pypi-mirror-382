# OrderExistingAccountDetails

The account basic information that this order has been created under. This is also the invoice owner of the subscriptions included in this order. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**basic_info** | [**AccountBasicInfo**](AccountBasicInfo.md) |  | [optional] 
**bill_to_contact** | [**Contact**](Contact.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_existing_account_details import OrderExistingAccountDetails

# TODO update the JSON string below
json = "{}"
# create an instance of OrderExistingAccountDetails from a JSON string
order_existing_account_details_instance = OrderExistingAccountDetails.from_json(json)
# print the JSON string representation of the object
print(OrderExistingAccountDetails.to_json())

# convert the object into a dict
order_existing_account_details_dict = order_existing_account_details_instance.to_dict()
# create an instance of OrderExistingAccountDetails from a dict
order_existing_account_details_from_dict = OrderExistingAccountDetails.from_dict(order_existing_account_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


