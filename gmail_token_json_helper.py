from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
flow = InstalledAppFlow.from_client_secrets_file(
    'gmail_credentials.json', SCOPES
    )
creds = flow.run_local_server(port=8080)
open('token.json','w').write(creds.to_json())
print('Wrote token.json')
