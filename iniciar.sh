#!/bin/bash
# Inicia o Onfly Analytics Dashboard

cd "$(dirname "$0")"

# Adiciona Homebrew ao PATH
export PATH="/opt/homebrew/bin:/Users/$(whoami)/Library/Python/3.9/bin:$PATH"

# Instala dependências se necessário
if ! python3 -c "import streamlit" 2>/dev/null; then
  echo "Instalando dependências..."
  pip3 install -r requirements.txt
fi

echo ""
echo "  Iniciando Onfly Analytics..."
echo "  Acesse: http://localhost:8501"
echo ""

streamlit run app.py
