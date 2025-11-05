# tests/verificar_sistema.py
import os
import sys
import importlib


def verificar_estrutura_sistema():
    """Verificar se toda a estrutura do sistema está correta"""

    print("🔍 VERIFICANDO ESTRUTURA DO SISTEMA")
    print("=" * 50)

    # Arquivos e pastas essenciais
    estrutura_necessaria = [
        'app.py',
        'config.py',
        'database.py',
        'models.py',
        'requirements.txt',
        'blueprints/',
        'blueprints/__init__.py',
        'blueprints/auth.py',
        'blueprints/main.py',
        'blueprints/servicos.py',
        'blueprints/api.py',
        'blueprints/chat.py',
        'blueprints/pagamentos.py',
        'blueprints/agendamentos.py',
        'blueprints/avaliacoes.py',
        'templates/',
        'templates/base.html',
        'static/',
        'static/css/',
        'static/js/'
    ]

    # Verificar arquivos
    for item in estrutura_necessaria:
        if os.path.exists(item):
            print(f"✅ {item}")
        else:
            print(f"❌ {item} - FALTANDO!")

    # Verificar imports
    print("\n🔧 VERIFICANDO IMPORTS...")
    modulos_verificar = [
        'flask', 'flask_login', 'sqlalchemy', 'werkzeug'
    ]

    for modulo in modulos_verificar:
        try:
            importlib.import_module(modulo)
            print(f"✅ {modulo}")
        except ImportError:
            print(f"❌ {modulo} - Não instalado!")

    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Execute: python tests/criar_dados_teste.py")
    print("2. Execute: python tests/test_completo.py")
    print("3. Verifique se todos os testes passam")
    print("4. Execute o sistema: python app.py")
    print("5. Acesse: http://localhost:5000")


if __name__ == "__main__":
    verificar_estrutura_sistema()