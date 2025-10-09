# PostPublicNotificationDefinitionRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**active** | **bool** | The status of the notification definition. The default value is &#x60;true&#x60;. | [optional] [default to True]
**associated_account** | **str** | Indicates with which type of account this notification is associated. Depending on your environment, you can use one of the following values:  * &#x60;Account.Id&#x60;: ID of the primary customer account related to the notification. It is also the default value.  * &#x60;ParentAccount.Id&#x60;: this option is available only if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled for your tenant.  * &#x60;SubscriptionOwnerAccount.Id&#x60;: this option is available if the base object of the notification is Order Action.   **Note:** before specifying this field, we recommend that you use [Data Source](https://knowledgecenter.zuora.com/Billing/Reporting/D_Data_Sources_and_Exports/C_Data_Source_Reference) to check the available types of accounts for the current notification.   | [optional] 
**callout** | [**PostPublicNotificationDefinitionRequestCallout**](PostPublicNotificationDefinitionRequestCallout.md) |  | [optional] 
**callout_active** | **bool** | The status of the callout action. The default value is &#x60;false&#x60;. | [optional] [default to False]
**communication_profile_id** | **str** | The profile that notification definition belongs to.    You can use the [Query Action](https://www.zuora.com/developer/api-references/api/operation/Action_Postquery) to get the communication profile Id. See the following request sample:   &#x60;{     \&quot;queryString\&quot;: \&quot;select Id, ProfileName from CommunicationProfile\&quot;  }&#x60;  If you do not pass the communicationProfileId, notification service will be automatically added to the &#39;Default Profile&#39;. | [optional] 
**description** | **str** | The description of the notification definition. | [optional] 
**email_active** | **bool** | The status of the email action. The default value is &#x60;false&#x60;. | [optional] [default to False]
**email_template_id** | **str** | The ID of the email template. If &#x60;emailActive&#x60; is &#x60;true&#x60;, an email template is required. And EventType of the email template MUST be the same as the eventType. | [optional] 
**event_type_name** | **str** | The name of the event type.   | 
**event_type_namespace** | **str** | The namespace of the &#x60;eventTypeName&#x60; field. The &#x60;eventTypeName&#x60; has the &#x60;user.notification&#x60; namespace by default.             For example, if you want to create a notification definition on the &#x60;OrderActionProcessed&#x60; event, you must specify &#x60;com.zuora.notification&#x60; for this field. | [optional] 
**filter_rule** | [**PostPublicNotificationDefinitionRequestFilterRule**](PostPublicNotificationDefinitionRequestFilterRule.md) |  | [optional] 
**filter_rule_params** | **Dict[str, str]** | The parameter values used to configure the filter rule.  | [optional] 
**name** | **str** | The name of the notification definition, unique per communication profile. | 

## Example

```python
from zuora_sdk.models.post_public_notification_definition_request import PostPublicNotificationDefinitionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostPublicNotificationDefinitionRequest from a JSON string
post_public_notification_definition_request_instance = PostPublicNotificationDefinitionRequest.from_json(json)
# print the JSON string representation of the object
print(PostPublicNotificationDefinitionRequest.to_json())

# convert the object into a dict
post_public_notification_definition_request_dict = post_public_notification_definition_request_instance.to_dict()
# create an instance of PostPublicNotificationDefinitionRequest from a dict
post_public_notification_definition_request_from_dict = PostPublicNotificationDefinitionRequest.from_dict(post_public_notification_definition_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


