# CreateBillingPreviewRunRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**assume_renewal** | **str** | Indicates whether to generate a preview of future invoice items and credit memo items with the assumption that the subscriptions are renewed.  nSet one of the following values in this field to decide how the assumption is applied in the billing preview.    * **All:** The assumption is applied to all the subscriptions. Zuora generates preview invoice item data and credit memo item data from the first day of the customer&#39;s next billing period to the target date.      * **None:** (Default) The assumption is not applied to the subscriptions. Zuora generates preview invoice item data and credit memo item data based on the current term end date and the target date.       * If the target date is later than the current term end date, Zuora generates preview invoice item data and credit memo item data from the first day of the customer&#39;s next billing period to the current term end date.   * If the target date is earlier than the current term end date, Zuora generates preview invoice item data and credit memeo item data from the first day of the customer&#39;s next billing period to the target date.    * **Autorenew:** The assumption is applied to the subscriptions that have auto-renew enabled. Zuora generates preview invoice item data and credit memo item data from the first day of the customer&#39;s next billing period to the target date.    **Note:**    - This field can only be used if the subscription renewal term is not set to 0.           - The credit memo item data is only available if you have Invoice Settlement feature enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   | [optional] 
**batch** | **str** | The customer batch to include in the billing preview run. If not specified, all customer batches are included.   **Note**: This field is not available if you set the &#x60;zuora-version&#x60; request header to &#x60;314.0&#x60; or later.  | [optional] 
**batches** | **str** | The customer batches to include in the billing preview run. You can specify multiple batches separated by comma. If not specified, all customer batches are included.  **Note**: This field is only available if you set the &#x60;zuora-version&#x60; request header to &#x60;314.0&#x60; or later.  | [optional] 
**charge_type_to_exclude** | **str** | The charge types to exclude from the forecast run.  **Possible values:** OneTime, Recurring, Usage, and any comma-separated combination of these values.  | [optional] 
**including_draft_items** | **bool** | Whether draft document items are included in the billing preview run. By default, draft document items are not included.  This field loads draft invoice items and credit memo items. The &#x60;chargeTypeToExclude&#x60;, &#x60;targetDate&#x60;, &#x60;includingEvergreenSubscription&#x60;, and &#x60;assumeRenewal&#x60; fields do not affect the behavior of the &#x60;includingDraftItems&#x60; field.  | [optional] 
**including_evergreen_subscription** | **bool** | Whether evergreen subscriptions are included in the billing preview run. By default, evergreen subscriptions are not included.  | [optional] 
**storage_option** | [**PostBillingPreviewRunParamStorageOption**](PostBillingPreviewRunParamStorageOption.md) |  | [optional] 
**target_date** | **date** | The target date for the billing preview run. The billing preview run generates preview invoice item data and credit memo item data from the first day of the customer&#39;s next billing period to the target date.   The value for the &#x60;targetDate&#x60; field must be in _&#x60;YYYY-MM-DD&#x60;_ format.  If the target date is later than the subscription current term end date, the preview invoice item data and credit memo item data is generated from the first day of the customer&#39;s next billing period to the current term end date. If you want to generate preview invoice item data and credit memo item data past the end of the subscription current term, specify the AssumeRenewal field in the request.  **Note:** The credit memo item data is only available if you have Invoice Settlement feature enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.  | 
**compared_billing_preview_run_id** | **str** | The ID of the billing preview run to compare with the current billing preview run. | [optional] 
**store_difference** | **bool** | Whether to store the difference between the current billing preview run and the compared billing preview run. The default value is &#x60;false&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.create_billing_preview_run_request import CreateBillingPreviewRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateBillingPreviewRunRequest from a JSON string
create_billing_preview_run_request_instance = CreateBillingPreviewRunRequest.from_json(json)
# print the JSON string representation of the object
print(CreateBillingPreviewRunRequest.to_json())

# convert the object into a dict
create_billing_preview_run_request_dict = create_billing_preview_run_request_instance.to_dict()
# create an instance of CreateBillingPreviewRunRequest from a dict
create_billing_preview_run_request_from_dict = CreateBillingPreviewRunRequest.from_dict(create_billing_preview_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


