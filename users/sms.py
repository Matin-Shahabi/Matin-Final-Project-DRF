import requests
from django.conf import settings

def send_otp_sms(phone, code):
    """
    ارسال کد OTP با استفاده از سرویس SMS.ir
    """
    url = "https://api.sms.ir/v1/send/verify"

    payload = {
        "mobile": phone,
        "templateId": int(settings.SMS_IR_PATTERN_ID),
        "parameters": [
            {"name": "code", "value": str(code)}
        ],
        "sender": settings.SMS_IR_LINE_NUMBER  # شماره اختصاصی ارسال کننده
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-KEY": settings.SMS_IR_API_KEY
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")
        return {"status": "error", "message": str(e)}

    if response.status_code != 200:
        print("SMS.ir returned error:", response.text)
        return {"status": "error", "message": response.text}

    result = response.json()
    if result.get("IsSuccessful"):
        print(f"OTP sent successfully to {phone}")
    else:
        print(f"Failed to send OTP to {phone}: {result}")

    return result
