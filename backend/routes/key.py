import secrets

# Generate a 256-bit secret
secret = secrets.token_hex(32)
print(secret)
