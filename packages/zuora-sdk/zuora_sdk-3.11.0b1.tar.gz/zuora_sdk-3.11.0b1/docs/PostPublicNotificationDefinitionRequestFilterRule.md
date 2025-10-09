# PostPublicNotificationDefinitionRequestFilterRule



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition** | **str** | The filter rule conditions, written in [JEXL](http://commons.apache.org/proper/commons-jexl/).  The rule might contain event context merge fields and data source merge fields. Data source merge fields must be from [the base object of the event or from the joined objects of the base object](https://knowledgecenter.zuora.com/DC_Developers/M_Export_ZOQL#Data_Sources_and_Objects). Notifications with invalid merge fields will fail to evaluate, thus will not be invoked. For example, to filter an invoice posted notification to only invoices with an amount over 1000, you would define the following condition:   &#x60;&#x60;&#x60;Invoice.Amount &gt; 1000&#x60;&#x60;&#x60;   There are conventions and keywords you need to be aware of. For example:   * &#x60;Invoice.Amount&#x60; refers to the &#x60;Amount&#x60; field of the Zuora object &#x60;Invoice&#x60;.   * Unlike Event Triggers, there is no access to variables with the &#x60;_old&#x60; suffix. Fields with the &#x60;_old&#x60; suffix are only available on Event Trigger conditions. | 
**description** | **str** | The description of the filter rule. | [optional] 
**parameters** | [**Dict[str, FilterRuleParameterDefinition]**](FilterRuleParameterDefinition.md) | The parameters of the filter rule and their name must match those in the filter rule. And all parameters must be defined in the event type payload. The name of parameters can&#39;t be duplicate. The following reserved keywords should not be used as a parameter name: &#x60;AttachmentList&#x60;, &#x60;RecipientList&#x60;, &#x60;RecipientType&#x60;, &#x60;Exceptions&#x60;, &#x60;OCP_OBJECT_TYPE&#x60;, &#x60;OCP_OBJECT_ID&#x60;, &#x60;OCP_TRIGGER_BY&#x60; | 

## Example

```python
from zuora_sdk.models.post_public_notification_definition_request_filter_rule import PostPublicNotificationDefinitionRequestFilterRule

# TODO update the JSON string below
json = "{}"
# create an instance of PostPublicNotificationDefinitionRequestFilterRule from a JSON string
post_public_notification_definition_request_filter_rule_instance = PostPublicNotificationDefinitionRequestFilterRule.from_json(json)
# print the JSON string representation of the object
print(PostPublicNotificationDefinitionRequestFilterRule.to_json())

# convert the object into a dict
post_public_notification_definition_request_filter_rule_dict = post_public_notification_definition_request_filter_rule_instance.to_dict()
# create an instance of PostPublicNotificationDefinitionRequestFilterRule from a dict
post_public_notification_definition_request_filter_rule_from_dict = PostPublicNotificationDefinitionRequestFilterRule.from_dict(post_public_notification_definition_request_filter_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


