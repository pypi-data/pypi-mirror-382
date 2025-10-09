import requests
from user_agent import generate_user_agent as ua
import pyfiglet
from rich.panel import Panel as P
from rich import print as p

def send_spam_email(email: str):
    """
    Sends a spam email to the specified email address.

    Args:
        email (str): The target email address to send spam to.
    """
    se = requests.Session()
    
    headers = {
        'authority': 'api.kidzapp.com',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://kidzapp.com',
        'referer': 'https://kidzapp.com/',
        'user-agent': str(ua()),
    }

    json_data = {
        'email': email,
        'sdk': 'web',
        'platform': 'desktop',
    }

    try:
        re = se.post('https://api.kidzapp.com/api/3.0/customlogin/', headers=headers, json=json_data).text
        if '"EMAIL SENT"' in re:
            p(P('SENT SPAM TO EMAIL'))
            return True
        else:
            p(P('There was an error. The connection was blocked for 10 minutes and then it came back on.'))
            return False
    except requests.exceptions.RequestException as e:
        p(P(f'An error occurred during the request: {e}'))
        return False


if __name__ == '__main__':
    print('-'*60)
    Logo = pyfiglet.figlet_format('               Email')
    print(Logo)
    print(' '*13,'-'*29)
    print(' '*13,'|',' '*1,'Tools For Spam Email',' '*2,'|')
    print(' '*13,'-'*29)
    
    target_email = input('Enter Email (For Sent Spam) : ')
    send_spam_email(target_email)

