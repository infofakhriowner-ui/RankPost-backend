
# How to generate a Fernet key (run in Python REPL)
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())  # copy into FERNET_KEY_BASE64 in .env
