# ContactSnapshotResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**address1** | **str** | The first line for the address of the contact, which is often a street address or business name. | [optional] 
**address2** | **str** | The second line for the address of the contact, which is mostly the locality. | [optional] 
**city** | **str** | The city for the address of the contact.  | [optional] 
**contact_id** | **str** | The Zuora ID of the contact who the snapshot belongs to.  | [optional] 
**country** | **str** | The country for the address of the contact.  | [optional] 
**county** | **str** | The county for the address of the contact. The field value might optionally be used by Zuora Tax to calculate county tax. | [optional] 
**description** | **str** | A description of the contact.  | [optional] 
**fax** | **str** | The fax number of the contact.  | [optional] 
**first_name** | **str** | The first name of the contact.  | [optional] 
**home_phone** | **str** | The home phone number of the contact.  | [optional] 
**id** | **str** | The unique ID of the contact snapshot.  | [optional] 
**last_name** | **str** | The last name of the contact.  | [optional] 
**mobile_phone** | **str** | The mobile phone number of the contact.  | [optional] 
**nickname** | **str** | A nickname for the contact.  | [optional] 
**other_phone** | **str** | An additional phone number for the contact.  | [optional] 
**other_phone_type** | [**PhoneType**](PhoneType.md) |  | [optional] 
**personal_email** | **str** | The personal email address of the contact.  | [optional] 
**postal_code** | **str** | The postal code for the address of the contact.  | [optional] 
**state** | **str** | The state or province for the address of the contact.  | [optional] 
**tax_region** | **str** | If using Zuora Tax rules.  | [optional] 
**work_email** | **str** | The business email address of the contact.  | [optional] 
**work_phone** | **str** | The business email address of the contact.  | [optional] 
**as_bill_to** | **bool** | Indicates the contact can as a bill to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_sold_to** | **bool** | Indicates the contact can as a sold to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_ship_to** | **bool** | Indicates the contact can as a ship to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 

## Example

```python
from zuora_sdk.models.contact_snapshot_response import ContactSnapshotResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ContactSnapshotResponse from a JSON string
contact_snapshot_response_instance = ContactSnapshotResponse.from_json(json)
# print the JSON string representation of the object
print(ContactSnapshotResponse.to_json())

# convert the object into a dict
contact_snapshot_response_dict = contact_snapshot_response_instance.to_dict()
# create an instance of ContactSnapshotResponse from a dict
contact_snapshot_response_from_dict = ContactSnapshotResponse.from_dict(contact_snapshot_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


