# CreateUsageRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** |  The ID of the account associated with the usage data. This field is only required if no value is specified for the &#x60;AccountNumber&#x60; field. **Character limit**: 32 **Values**: a valid account ID. | [optional] 
**account_number** | **str** |  The number of the account associated with the usage data. This field is only required if no value is specified for the &#x60;AccountId&#x60; field. **Character limit**: 50 **Values**: a valid account number. | [optional] 
**subscription_id** | **str** | The original ID of the subscription that contains the fees related to the usage data.    The ID of a subscription might change when you create amendments to the subscription. It is good practice to use the unique subscription number that you can specify in the &#x60;SubscriptionNumber&#x60; field. | [optional] 
**subscription_number** | **str** | The unique identifier number of the subscription that contains the fees related to the usage data.   It is good practice to use this field when creating usage records. | [optional] 
**charge_id** | **str** |  The OrginalId of the rate plan charge related to the usage record, e.g., &#x60;2c9081a03c63c94c013c6873357a0117&#x60; **Character limit**: 32 **Values**: a valid rate plan charge OriginalID.  | [optional] 
**charge_number** | **str** | A unique number for the rate plan charge related to the usage record. For example, C-00000007. | [optional] 
**start_date_time** | **datetime** |  The start date and time of a range of time when usage is tracked. Zuora uses this field value to determine the usage date. Unlike the &#x60;EndDateTime&#x60;, the &#x60;StartDateTime&#x60; field does affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value | 
**end_date_time** | **datetime** |  The end date and time of a range of time when usage is tracked. Use this field for reporting; this field doesn&#39;t affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value. | [optional] 
**uom** | **str** |  Specifies the units to measure usage. Units of measure are configured in the web-based UI. Your values depend on your configuration in **Billing Settings**. **Character limit**: **Values**: a valid unit of measure | 
**quantity** | **float** |  Indicates the number of units used. **Character limit**: 16 **Values**: a valid decimal amount equal to or greater than 0 | 
**description** | **str** | A description of the usage record.  | [optional] 

## Example

```python
from zuora_sdk.models.create_usage_request import CreateUsageRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateUsageRequest from a JSON string
create_usage_request_instance = CreateUsageRequest.from_json(json)
# print the JSON string representation of the object
print(CreateUsageRequest.to_json())

# convert the object into a dict
create_usage_request_dict = create_usage_request_instance.to_dict()
# create an instance of CreateUsageRequest from a dict
create_usage_request_from_dict = CreateUsageRequest.from_dict(create_usage_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


