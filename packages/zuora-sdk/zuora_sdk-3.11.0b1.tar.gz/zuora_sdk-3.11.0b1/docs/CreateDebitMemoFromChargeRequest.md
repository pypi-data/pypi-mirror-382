# CreateDebitMemoFromChargeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the account associated with the debit memo.  **Note**: When creating debit memos from product rate plan charges, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account. | [optional] 
**account_number** | **str** | The number of the account associated with the debit memo.  **Note**: When creating debit memos from product rate plan charges, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account. | [optional] 
**auto_pay** | **bool** | Whether debit memos are automatically picked up for processing in the corresponding payment run.   By default, debit memos are automatically picked up for processing in the corresponding payment run.  | [optional] 
**auto_post** | **bool** | Whether to automatically post the debit memo after it is created.   Setting this field to &#x60;true&#x60;, you do not need to separately call the [Post a debit memo](https://www.zuora.com/developer/api-references/api/operation/Put_PostDebitMemo) operation to post the debit memo.  | [optional] [default to False]
**charges** | [**List[DebitMemoItemFromChargeDetail]**](DebitMemoItemFromChargeDetail.md) | Container for product rate plan charges. The maximum number of items is 1,000. | 
**comment** | **str** | Comments about the debit memo. | [optional] 
**custom_rates** | [**List[CustomRates]**](CustomRates.md) | It contains Home currency and Reporting currency custom rates currencies. The maximum number of items is 2 (you can pass the Home currency item or Reporting currency item or both).  **Note**: The API custom rate feature is permission controlled. | [optional] 
**due_date** | **date** | The date by which the payment for the debit memo is due, in &#x60;yyyy-mm-dd&#x60; format. | [optional] 
**effective_date** | **date** | The date when the debit memo takes effect. | [optional] 
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code. | [optional] 
**currency** | **str** | The code of a currency as defined in Billing Settings through the Zuora UI.  If you do not specify a currency during debit memo creation, the default account currency is applied. The currency that you specify in the request must be configured and activated in Billing Settings.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Multiple_Currencies\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Multiple Currencies&lt;/a&gt; feature in the **Early Adopter** phase enabled.  | [optional] 
**number** | **str** | A customized memo number with the following format requirements:  - Max length: 32 - Acceptable characters: a-z,A-Z,0-9,-,_,  The value must be unique in the system, otherwise it may cause issues with bill runs and subscribe/amend. If it is not provided, memo number will be auto-generated.  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the debit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the debit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.create_debit_memo_from_charge_request import CreateDebitMemoFromChargeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateDebitMemoFromChargeRequest from a JSON string
create_debit_memo_from_charge_request_instance = CreateDebitMemoFromChargeRequest.from_json(json)
# print the JSON string representation of the object
print(CreateDebitMemoFromChargeRequest.to_json())

# convert the object into a dict
create_debit_memo_from_charge_request_dict = create_debit_memo_from_charge_request_instance.to_dict()
# create an instance of CreateDebitMemoFromChargeRequest from a dict
create_debit_memo_from_charge_request_from_dict = CreateDebitMemoFromChargeRequest.from_dict(create_debit_memo_from_charge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


