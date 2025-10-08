# amazon_advertising

Amazon Advertising SDK

## Basic Info

``` python
client_id = 'XXXX'
client_secret = 'XXXXX'
```

## Api Authorization

``` python
from client.auth import ZADAuthClient

auth_client = ZADAuthClient(client_id, client_secret, 'SANDBOX')
```

###  Step 1: Get an authorization code

``` python
redirect_uri = 'http://localhost/'
auth_url = auth_client.authorization_url(redirect_uri) 
```

Next, paste the URL in your browser's address window. Navigate to the URL. Sign in, and Grant application access

If you selected Allow in consent form, your browser is redirected to the provided redirect_uri.

eg: `http://localhost/?code=xxxxxxxxxxxxxxxxxxx&scope=cpc_advertising%3Acampaign_management`

Make note of the value of the code query parameter. The code query parameter is the authorization code that is exchanged for the authorization token and the refresh tokens in the next step.

### Step 2: Call the authorization URL to request authorization and refresh tokens

``` python
auth_info = auth_client.token.get_token(code, redirect_uri)
```

Get authorization information, for example:

``` python
{
    "access_token": "",
    "refresh_token": "",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### Step 3: Refresh token

``` python
	auth_info = auth_client.token.refresh_token(refresh_token)
```

## Profiles

``` python
from client.auth import ZADProfileClient

profile_client = ZADProfileClient(client_id, access_token, "SANDBOX")

profiles = profile_client.profiles.list()

profile = profile_client.profiles.get(profile_id)

```

## Services

``` python
from client.service import ZADServiceClient

client = ZADServiceClient(client_id, access_token, profile_id='xxxxxx', country="SANDBOX")

```