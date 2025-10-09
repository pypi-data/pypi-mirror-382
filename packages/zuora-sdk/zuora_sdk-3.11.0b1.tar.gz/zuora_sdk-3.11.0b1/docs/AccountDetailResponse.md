# AccountDetailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**basic_info** | [**AccountBasicInfo**](AccountBasicInfo.md) |  | [optional] 
**bill_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**billing_and_payment** | [**AccountBillingAndPayment**](AccountBillingAndPayment.md) |  | [optional] 
**metrics** | [**AccountMetrics**](AccountMetrics.md) |  | [optional] 
**sold_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**ship_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 
**metrics_data** | [**List[AccountMetrics]**](AccountMetrics.md) | Container for account metrics of different currencies.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Multiple_Currencies\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Multiple Currencies&lt;/a&gt; feature in the **Early Adopter** phase enabled.  | [optional] 
**einvoice_profile** | [**AccountEInvoiceProfile**](AccountEInvoiceProfile.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.account_detail_response import AccountDetailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AccountDetailResponse from a JSON string
account_detail_response_instance = AccountDetailResponse.from_json(json)
# print the JSON string representation of the object
print(AccountDetailResponse.to_json())

# convert the object into a dict
account_detail_response_dict = account_detail_response_instance.to_dict()
# create an instance of AccountDetailResponse from a dict
account_detail_response_from_dict = AccountDetailResponse.from_dict(account_detail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


