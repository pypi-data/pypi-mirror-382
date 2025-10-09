# GetUsageResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Object identifier. | [optional] 
**account_id** | **str** |  The ID of the account associated with the usage data. This field is required if no value is specified for the &#x60;AccountNumber&#x60; field. **Character limit**: 32 **Values**: a valid account ID | [optional] 
**account_number** | **str** |  The number of the account associated with the usage data. This field is required if no value is specified for the &#x60;AccountId&#x60; field. **Character limit**: 50 **Values**: a valid account number | [optional] 
**subscription_id** | **str** |  The original ID of the subscription that contains the fees related to the usage data. **Character limit**: 32 **Values**: a valid subscription ID | [optional] 
**subscription_number** | **str** | The unique identifier number of the subscription that contains the fees related to the usage data. | [optional] 
**charge_id** | **str** |  The OrginalId of the rate plan charge related to the usage record, e.g., &#x60;2c9081a03c63c94c013c6873357a0117&#x60; **Character limit**: 32 **Values**: a valid rate plan charge OriginalID  | [optional] 
**charge_number** | **str** | Number of the rate-plan charge that pays for this usage.  | [optional] 
**start_date_time** | **datetime** |  The start date and time of a range of time when usage is tracked. Zuora uses this field value to determine the usage date. Unlike the &#x60;EndDateTime&#x60;, the &#x60;StartDateTime&#x60; field does affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value | [optional] 
**end_date_time** | **datetime** |  The end date and time of a range of time when usage is tracked. Use this field for reporting; this field doesn&#39;t affect usage calculation. **Character limit**: 29 **Values**: a valid date and time value | [optional] 
**uom** | **str** |  Specifies the units to measure usage. Units of measure are configured in the web-based UI. Your values depend on your configuration in **Billing Settings**. **Character limit**: **Values**: a valid unit of measure | [optional] 
**quantity** | **float** |  Indicates the number of units used. **Character limit**: 16 **Values**: a valid decimal amount equal to or greater than 0 | [optional] 
**source_type** | **str** |  Indicates if the usage records were imported from the web-based UI or the API. **Character limit**: 6 **Values**: automatically generated to be one of the following values: &#x60;API&#x60;, &#x60;Import&#x60; | [optional] 
**rbe_status** | **str** |  Indicates if the rating and billing engine (RBE) processed usage data for an invoice. **Character limit**: 9 **Values**: automatically generated to be one of the following values: &#x60;Importing&#x60;, &#x60;Pending&#x60;, &#x60;Processed&#x60; | [optional] 
**description** | **str** | A description of the usage record.  | [optional] 
**created_by_id** | **str** |  The user ID of the person who uploaded the usage records. **Character limit**: 32 **Values**: automatically generated | [optional] 
**created_date** | **datetime** |  The date when the usage was generated. **Character limit**: 29 **Values**: automatically generated | [optional] 
**updated_by_id** | **str** |  The ID of the user who last updated the usage upload. **Character limit**: 32 **Values**: automatically generated | [optional] 
**updated_date** | **datetime** |  The date when the usage upload was last updated. **Character limit**: 29 **Values**: automatically generated | [optional] 
**submission_date_time** | **datetime** | Date when usage was submitted.  | [optional] 

## Example

```python
from zuora_sdk.models.get_usage_response import GetUsageResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetUsageResponse from a JSON string
get_usage_response_instance = GetUsageResponse.from_json(json)
# print the JSON string representation of the object
print(GetUsageResponse.to_json())

# convert the object into a dict
get_usage_response_dict = get_usage_response_instance.to_dict()
# create an instance of GetUsageResponse from a dict
get_usage_response_from_dict = GetUsageResponse.from_dict(get_usage_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


