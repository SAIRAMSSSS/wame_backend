"""
Test OAuth credentials
Run this to verify your Google OAuth setup
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("GOOGLE OAUTH CREDENTIALS TEST")
print("=" * 60)

client_id = os.environ.get('GOOGLE_CLIENT_ID')
client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')

print(f"\n1. Client ID:")
print(f"   {client_id}")
print(f"   Length: {len(client_id) if client_id else 0} characters")

print(f"\n2. Client Secret:")
print(f"   {client_secret}")
print(f"   Length: {len(client_secret) if client_secret else 0} characters")

print(f"\n3. Redirect URI:")
print(f"   {redirect_uri}")

print("\n" + "=" * 60)
print("CHECKS:")
print("=" * 60)

# Check if credentials are set
if not client_id or client_id == 'YOUR_GOOGLE_CLIENT_ID':
    print("❌ Client ID is not set properly!")
else:
    print("✅ Client ID is set")

if not client_secret or client_secret == 'YOUR_GOOGLE_CLIENT_SECRET':
    print("❌ Client Secret is not set properly!")
else:
    print("✅ Client Secret is set")

if not redirect_uri:
    print("❌ Redirect URI is not set!")
else:
    print("✅ Redirect URI is set")

print("\n" + "=" * 60)
print("NEXT STEPS:")
print("=" * 60)
print("\n1. Go to Google Cloud Console:")
print("   https://console.cloud.google.com/apis/credentials")
print("\n2. Click on your OAuth 2.0 Client ID")
print("\n3. Verify the credentials match:")
print(f"   - Client ID should be: {client_id}")
print(f"   - Client secret should be: {client_secret}")
print(f"   - Redirect URI should include: {redirect_uri}")
print("\n4. If they don't match, copy the correct values to .env file")
print("\n" + "=" * 60)
