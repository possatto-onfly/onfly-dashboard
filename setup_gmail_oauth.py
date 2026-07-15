#!/usr/bin/env python3
"""
Executa UMA VEZ para obter o refresh_token do Gmail OAuth.

Pré-requisitos:
  1. Crie um projeto no https://console.cloud.google.com
  2. Ative a Gmail API
  3. Crie credenciais OAuth 2.0 (tipo: Desktop App)
  4. Baixe o arquivo JSON e renomeie para client_secret.json
     nesta mesma pasta.

Uso:
  pip install google-auth-oauthlib
  python setup_gmail_oauth.py

Ao final, copie as 3 linhas para .streamlit/secrets.toml
"""
import json, sys, os

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Instale: pip install google-auth-oauthlib")
    sys.exit(1)

SECRET_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
if not os.path.exists(SECRET_FILE):
    print(f"Arquivo não encontrado: {SECRET_FILE}")
    print("Baixe as credenciais OAuth no Google Cloud Console e salve como client_secret.json aqui.")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

flow = InstalledAppFlow.from_client_secrets_file(SECRET_FILE, SCOPES)
creds = flow.run_local_server(port=0)

print("\n✅ Autenticação concluída! Adicione estas 3 linhas ao .streamlit/secrets.toml:\n")
print(f'GMAIL_CLIENT_ID     = "{creds.client_id}"')
print(f'GMAIL_CLIENT_SECRET = "{creds.client_secret}"')
print(f'GMAIL_REFRESH_TOKEN = "{creds.refresh_token}"')
print()
