# Shared Types

```python
from surge.types import Error
```

# Accounts

Types:

```python
from surge.types import Account, AccountStatus, Organization
```

Methods:

- <code title="post /accounts">client.accounts.<a href="./src/surge/resources/accounts.py">create</a>(\*\*<a href="src/surge/types/account_create_params.py">params</a>) -> <a href="./src/surge/types/account.py">Account</a></code>
- <code title="patch /accounts/{id}">client.accounts.<a href="./src/surge/resources/accounts.py">update</a>(id, \*\*<a href="src/surge/types/account_update_params.py">params</a>) -> <a href="./src/surge/types/account.py">Account</a></code>
- <code title="get /accounts/{account_id}/status">client.accounts.<a href="./src/surge/resources/accounts.py">retrieve_status</a>(account_id, \*\*<a href="src/surge/types/account_retrieve_status_params.py">params</a>) -> <a href="./src/surge/types/account_status.py">AccountStatus</a></code>

# Blasts

Types:

```python
from surge.types import Blast
```

Methods:

- <code title="post /accounts/{account_id}/blasts">client.blasts.<a href="./src/surge/resources/blasts.py">create</a>(account_id, \*\*<a href="src/surge/types/blast_create_params.py">params</a>) -> <a href="./src/surge/types/blast.py">Blast</a></code>

# Campaigns

Types:

```python
from surge.types import Campaign
```

Methods:

- <code title="post /accounts/{account_id}/campaigns">client.campaigns.<a href="./src/surge/resources/campaigns.py">create</a>(account_id, \*\*<a href="src/surge/types/campaign_create_params.py">params</a>) -> <a href="./src/surge/types/campaign.py">Campaign</a></code>

# Contacts

Types:

```python
from surge.types import Contact
```

Methods:

- <code title="post /accounts/{account_id}/contacts">client.contacts.<a href="./src/surge/resources/contacts.py">create</a>(account_id, \*\*<a href="src/surge/types/contact_create_params.py">params</a>) -> <a href="./src/surge/types/contact.py">Contact</a></code>
- <code title="get /contacts/{id}">client.contacts.<a href="./src/surge/resources/contacts.py">retrieve</a>(id) -> <a href="./src/surge/types/contact.py">Contact</a></code>
- <code title="patch /contacts/{id}">client.contacts.<a href="./src/surge/resources/contacts.py">update</a>(id, \*\*<a href="src/surge/types/contact_update_params.py">params</a>) -> <a href="./src/surge/types/contact.py">Contact</a></code>

# Messages

Types:

```python
from surge.types import Message
```

Methods:

- <code title="post /accounts/{account_id}/messages">client.messages.<a href="./src/surge/resources/messages.py">create</a>(account_id, \*\*<a href="src/surge/types/message_create_params.py">params</a>) -> <a href="./src/surge/types/message.py">Message</a></code>

# PhoneNumbers

Types:

```python
from surge.types import PhoneNumber
```

Methods:

- <code title="post /accounts/{account_id}/phone_numbers">client.phone_numbers.<a href="./src/surge/resources/phone_numbers.py">purchase</a>(account_id, \*\*<a href="src/surge/types/phone_number_purchase_params.py">params</a>) -> <a href="./src/surge/types/phone_number.py">PhoneNumber</a></code>

# Users

Types:

```python
from surge.types import User, UserTokenResponse
```

Methods:

- <code title="post /accounts/{account_id}/users">client.users.<a href="./src/surge/resources/users.py">create</a>(account_id, \*\*<a href="src/surge/types/user_create_params.py">params</a>) -> <a href="./src/surge/types/user.py">User</a></code>
- <code title="get /users/{id}">client.users.<a href="./src/surge/resources/users.py">retrieve</a>(id) -> <a href="./src/surge/types/user.py">User</a></code>
- <code title="patch /users/{id}">client.users.<a href="./src/surge/resources/users.py">update</a>(id, \*\*<a href="src/surge/types/user_update_params.py">params</a>) -> <a href="./src/surge/types/user.py">User</a></code>
- <code title="post /users/{user_id}/tokens">client.users.<a href="./src/surge/resources/users.py">create_token</a>(user_id, \*\*<a href="src/surge/types/user_create_token_params.py">params</a>) -> <a href="./src/surge/types/user_token_response.py">UserTokenResponse</a></code>

# Verifications

Types:

```python
from surge.types import Verification, VerificationCheck
```

Methods:

- <code title="post /verifications">client.verifications.<a href="./src/surge/resources/verifications.py">create</a>(\*\*<a href="src/surge/types/verification_create_params.py">params</a>) -> <a href="./src/surge/types/verification.py">Verification</a></code>
- <code title="post /verifications/{id}/checks">client.verifications.<a href="./src/surge/resources/verifications.py">check</a>(id, \*\*<a href="src/surge/types/verification_check_params.py">params</a>) -> <a href="./src/surge/types/verification_check.py">VerificationCheck</a></code>

# Webhooks

Types:

```python
from surge.types import (
    CallEndedWebhookEvent,
    CampaignApprovedWebhookEvent,
    ContactOptedInWebhookEvent,
    ContactOptedOutWebhookEvent,
    ConversationCreatedWebhookEvent,
    MessageDeliveredWebhookEvent,
    MessageFailedWebhookEvent,
    MessageReceivedWebhookEvent,
    MessageSentWebhookEvent,
    UnwrapWebhookEvent,
)
```
