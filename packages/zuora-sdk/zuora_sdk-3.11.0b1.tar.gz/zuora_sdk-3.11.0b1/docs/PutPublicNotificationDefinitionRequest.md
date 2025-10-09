# PutPublicNotificationDefinitionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the notification definition. The default value is &#x60;true&#x60;. | [optional] [default to True]
**associated_account** | **str** | Indicates with which type of account this notification is associated. Depending on your environment, you can use one of the following values:  * &#x60;Account.Id&#x60;: ID of the primary customer account related to the notification. It is also the default value.  * &#x60;ParentAccount.Id&#x60;: this option is available only if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled for your tenant.  * &#x60;SubscriptionOwnerAccount.Id&#x60;: this option is available if the base object of the notification is Order Action.   **Note:** before specifying this field, we recommend that you use [Data Source](https://knowledgecenter.zuora.com/Billing/Reporting/D_Data_Sources_and_Exports/C_Data_Source_Reference) to check the available types of accounts for the current notification.   | [optional] 
**callout** | [**PutPublicNotificationDefinitionRequestCallout**](PutPublicNotificationDefinitionRequestCallout.md) |  | [optional] 
**callout_active** | **bool** | The status of the callout action. The default value is &#x60;false&#x60;. | [optional] [default to False]
**communication_profile_id** | **str** | The profile that notification definition belongs to. If you want to update the notification to a system notification, you should pass &#39;SystemNotification&#39;. &#39;  | [optional] 
**description** | **str** | The description of the notification definition. | [optional] 
**email_active** | **bool** | The status of the email action. The default value is &#x60;false&#x60;. | [optional] [default to False]
**email_template_id** | **str** | The ID of the email template. If emailActive is updated from  false to true, an email template is required, and the EventType of  the email template MUST be the same as the EventType of the notification definition. | [optional] 
**filter_rule** | [**PutPublicNotificationDefinitionRequestFilterRule**](PutPublicNotificationDefinitionRequestFilterRule.md) |  | [optional] 
**filter_rule_params** | **Dict[str, str]** | The parameter values used to configure the filter rule.  | [optional] 
**name** | **str** | The name of the notification definition, which is unique in the profile. | [optional] 

## Example

```python
from zuora_sdk.models.put_public_notification_definition_request import PutPublicNotificationDefinitionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PutPublicNotificationDefinitionRequest from a JSON string
put_public_notification_definition_request_instance = PutPublicNotificationDefinitionRequest.from_json(json)
# print the JSON string representation of the object
print(PutPublicNotificationDefinitionRequest.to_json())

# convert the object into a dict
put_public_notification_definition_request_dict = put_public_notification_definition_request_instance.to_dict()
# create an instance of PutPublicNotificationDefinitionRequest from a dict
put_public_notification_definition_request_from_dict = PutPublicNotificationDefinitionRequest.from_dict(put_public_notification_definition_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


