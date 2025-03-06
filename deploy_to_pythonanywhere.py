import requests
import os
import subprocess

username = os.getenv('PA_USERNAME')
token = os.getenv('PA_API_TOKEN')

# Define the API endpoint
api_url = f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/'

# Get the list of web apps
response = requests.get(api_url, headers={'Authorization': f'Token {token}'})
if response.status_code == 200:
    webapps = response.json()
    for webapp in webapps:
        print(f'Found web app: {webapp["domain_name"]}')
        # Reload the web app
        reload_url = f'{api_url}{webapp["domain_name"]}/reload/'
        reload_response = requests.post(reload_url, headers={'Authorization': f'Token {token}'})
        if reload_response.status_code == 200:
            print(f'Successfully reloaded {webapp["domain_name"]}')
        else:
            print(f'Failed to reload {webapp["domain_name"]}: {reload_response.content}')
else:
    print(f'Failed to get web apps: {response.content}')

# Push the latest code to PythonAnywhere
subprocess.run(['git', 'pull', 'origin', 'main'])
