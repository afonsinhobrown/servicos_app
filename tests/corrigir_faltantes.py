# tests/corrigir_faltantes.py
import os
import sys


def criar_estrutura_faltante():
    print("🔧 CRIANDO ESTRUTURA FALTANTE...")

    # Criar pastas necessárias
    pastas = [
        'templates/servicos',
        'templates/static',
        'templates/agendamentos',
        'templates/chat',
        'templates/pagamentos',
        'templates/avaliacoes'
    ]

    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"✅ Criada pasta: {pasta}")

    # Criar templates básicos
    templates = {
        'templates/servicos/buscar.html': '''{% extends "base.html" %}
{% block title %}Buscar Serviços{% endblock %}
{% block content %}
<div class="container py-5">
    <div class="text-center">
        <h1>Buscar Serviços</h1>
        <p>Funcionalidade em desenvolvimento</p>
    </div>
</div>
{% endblock %}''',

        'templates/static/sobre.html': '''{% extends "base.html" %}
{% block title %}Sobre{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Sobre</h1>
    <p>Plataforma ServiçosPro - Conectando profissionais e clientes em Moçambique.</p>
</div>
{% endblock %}''',

        'templates/static/contato.html': '''{% extends "base.html" %}
{% block title %}Contato{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Contato</h1>
    <p>Entre em contato conosco.</p>
</div>
{% endblock %}'''
    }

    for arquivo, conteudo in templates.items():
        if not os.path.exists(arquivo):
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f"✅ Criado: {arquivo}")

    print("🎯 ESTRUTURA COMPLETA!")


if __name__ == "__main__":
    criar_estrutura_faltante()