# CreateCreditMemoFromChargeRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the account associated with the credit memo.  **Note**: When creating credit memos from product rate plan charges, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account.  | [optional] 
**account_number** | **str** | The number of the customer account associated with the credit memo.  **Note**: When creating credit memos from product rate plan charges, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account.  | [optional] 
**auto_post** | **bool** | Whether to automatically post the credit memo after it is created.  Setting this field to &#x60;true&#x60;, you do not need to separately call the [Post a credit memo](https://www.zuora.com/developer/api-references/api/operation/Put_PostCreditMemo) operation to post the credit memo.  | [optional] [default to False]
**charges** | [**List[CreditMemoItemFromChargeDetail]**](CreditMemoItemFromChargeDetail.md) | Container for product rate plan charges. The maximum number of items is 1,000.  | 
**comment** | **str** | Comments about the credit memo.  | [optional] 
**custom_rates** | [**List[CustomRates]**](CustomRates.md) | It contains Home currency and Reporting currency custom rates currencies. The maximum number of items is 2 (you can pass the Home currency item or Reporting currency item or both).  **Note**: The API custom rate feature is permission controlled.  | [optional] 
**effective_date** | **date** | The date when the credit memo takes effect.  | [optional] 
**exclude_from_auto_apply_rules** | **bool** | Whether the credit memo is excluded from the rule of automatically applying unapplied credit memos to invoices and debit memos during payment runs. If you set this field to &#x60;true&#x60;, a payment run does not pick up this credit memo or apply it to other invoices or debit memos. | [optional] [default to False]
**reason_code** | **str** | A code identifying the reason for the transaction. The value must be an existing reason code or empty. If you do not specify a value, Zuora uses the default reason code. | [optional] 
**currency** | **str** | The code of a currency as defined in Billing Settings through the Zuora UI.  If you do not specify a currency during credit memo creation, the default account currency is applied. The currency that you specify in the request must be configured and activated in Billing Settings.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Multiple_Currencies\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Multiple Currencies&lt;/a&gt; feature in the **Early Adopter** phase enabled.  | [optional] 
**number** | **str** | A customized memo number with the following format requirements:  - Max length: 32 - Acceptable characters: a-z,A-Z,0-9,-,_,  The value must be unique in the system, otherwise it may cause issues with bill runs and subscribe/amend. If it is not provided, memo number will be auto-generated.  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the credit memo&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**origin__ns** | **str** | Origin of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the credit memo was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**transaction__ns** | **str** | Related transaction in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 

## Example

```python
from zuora_sdk.models.create_credit_memo_from_charge_request import CreateCreditMemoFromChargeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCreditMemoFromChargeRequest from a JSON string
create_credit_memo_from_charge_request_instance = CreateCreditMemoFromChargeRequest.from_json(json)
# print the JSON string representation of the object
print(CreateCreditMemoFromChargeRequest.to_json())

# convert the object into a dict
create_credit_memo_from_charge_request_dict = create_credit_memo_from_charge_request_instance.to_dict()
# create an instance of CreateCreditMemoFromChargeRequest from a dict
create_credit_memo_from_charge_request_from_dict = CreateCreditMemoFromChargeRequest.from_dict(create_credit_memo_from_charge_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


