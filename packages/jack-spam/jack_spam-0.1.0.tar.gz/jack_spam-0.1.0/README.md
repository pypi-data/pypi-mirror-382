# jack_spam

A simple Python library for sending OTP (One-Time Password) requests to the OSN Plus service.

## Installation

```bash
pip install jack_spam
```

## Usage

```python
from jack_spam import send_otp_spam

# Send 5 OTP requests to a specific email
send_otp_spam("example@example.com", attempts=5)
```

## License

This project is licensed under the MIT License.

