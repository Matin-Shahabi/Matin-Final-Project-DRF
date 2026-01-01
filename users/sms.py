import requests
from django.conf import settings

def send_otp_pattern(phone, otp):
    """
    ارسال OTP با الگوی فراز اس‌ام‌اس - دقیقاً طبق payload دوستت
    """
    url = "https://edge.ippanel.com/v1/api/send"  # URL ثابت فراز

    headers = {
        "Authorization":settings.FARAZSMS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "sending_type": "pattern",
        "from_number": "+983000505",
        "code": settings.FARAZSMS_PATTERN_CODE,
        "recipients": [f"{phone}"],
        "params": {"code": f"{otp}"},
        "phonebook": {
            "id": 1,
            "name": None,
            "pre": None,
            "email": "",
            "options": "",
        },
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        result = response.json()
        print("پاسخ کامل فراز اس‌ام‌اس:", result)

        # وضعیت‌های موفقیت در فراز معمولاً status = 0 یا 200
        if response.status_code == 200 and result.get("status") in [0, "0"]:
            return True
        else:
            print("خطا از سمت فراز:", result.get("message", "نامشخص"))
            return False

    except requests.exceptions.Timeout:
        print("تایم‌اوت در ارسال به فراز اس‌ام‌اس")
        return False
    except requests.exceptions.RequestException as e:
        print("خطا در ارتباط با فراز:", e)
        return False
    except Exception as e:
        print("خطای غیرمنتظره:", e)
        return False