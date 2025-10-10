# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Campaign"]


class Campaign(BaseModel):
    id: str
    """The campaign ID"""

    consent_flow: str
    """
    A string explaining the method through which end users will opt in to receive
    messages from the brand. Typically this should include URLs for opt-in forms or
    screenshots that might be helpful in explaining the flow to someone unfamiliar
    with the organization's purpose.
    """

    description: str
    """
    An explanation of the organization's purpose and how it will be using text
    messaging to accomplish that purpose.
    """

    includes: List[Literal["links", "phone_numbers", "age_gated", "direct_lending"]]
    """A list of properties that this campaign should include.

    These properties can be any of the following values:

    - `links` - whether the campaign might send links in messages
    - `phone_numbers` - whether the campaign might send phone numbers in messages
    - `age_gated` - whether the campaign contains age gated content (controlled
      substances or adult content)
    - `direct_lending` - whether the campaign contains content related to direct
      lending or other loan arrangements
    """

    message_samples: List[str]
    """
    An array of 2-5 strings with examples of the messages that will be sent from
    this campaign. Typically the first sample should be a compliance message like
    `You are now opted in to messages from {brand name}. Frequency varies. Msg&data rates apply. Reply STOP to opt out.`
    These samples don't necessarily need to be the only templates that will be used
    for the campaign, but they should reflect the purpose of the messages that will
    be sent. Any variable content can be reflected by wrapping it in square brackets
    like `[customer name]`.
    """

    privacy_policy_url: str
    """The URL of the privacy policy for the brand in question.

    This may be a shared privacy policy if it's the policy that is displayed to end
    users when they opt in to messaging.
    """

    use_cases: List[
        Literal[
            "account_notification",
            "customer_care",
            "delivery_notification",
            "fraud_alert",
            "higher_education",
            "marketing",
            "polling_voting",
            "public_service_announcement",
            "security_alert",
            "two_factor_authentication",
        ]
    ]
    """A list containing 1-5 types of messages that will be sent with this campaign.

    The following use cases are typically available to all brands:

    - `account_notification` - For sending reminders, alerts, and general
      account-related notifications like booking confirmations or appointment
      reminders.
    - `customer_care` - For account support, troubleshooting, and general customer
      service communication.
    - `delivery_notification` - For notifying customers about the status of product
      or service deliveries.
    - `fraud_alert` - For warning customers about suspicious or potentially
      fraudulent activity.
    - `higher_education` - For messaging related to colleges, universities, and
      school districts outside of K–12.
    - `marketing` - For promotional or advertising messages intended to market
      products or services.
    - `polling_voting` - For conducting surveys, polls, or voting-related messaging.
    - `public_service_announcement` - For raising awareness about social issues or
      important public information.
    - `security_alert` - For alerts related to potential security breaches or
      compromised systems requiring user action.
    - `two_factor_authentication` - For sending one-time passwords or verification
      codes for login or password reset.

    For access to special use cases not shown here, reach out to support@surge.app.
    """

    volume: Literal["high", "low"]
    """This will be one of the following:

    - `low` - The campaign will be allowed to send up to 2000 SMS segments to
      T-Mobile customers each day. In this case your platform will be charged for
      the setup fee for a low volume number upon receipt of the API request.
    - `high` - The campaign will be allowed to send up to 200k SMS segments to
      T-Mobile customers each day, depending on the trust score assigned by The
      Campaign Registry. Your platform will be charged for the setup fee for a high
      volume number upon receipt of the API request, and phone numbers will be
      charged as high volume numbers going forward.
    """

    link_sample: Optional[str] = None
    """A sample link that might be sent by this campaign.

    If links from other domains are sent through this campaign, they are much more
    likely to be filtered by the carriers. If link shortening is enabled for the
    account, the link shortener URL will be used instead of what is provided. Reach
    out to support if you would like to disable automatic link shortening.
    """

    terms_and_conditions_url: Optional[str] = None
    """
    The URL of the terms and conditions presented to end users when they opt in to
    messaging. These terms and conditions may be shared among all of a platform's
    customers if they're the terms that are presented to end users when they opt in
    to messaging.
    """
