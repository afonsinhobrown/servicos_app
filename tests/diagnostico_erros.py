# tests/diagnostico_erros.py
import requests
import json

BASE_URL = "http://localhost:5000"


def diagnostico_completo():
    print("🔍 DIAGNÓSTICO DE ERROS - SERVIÇOSPRO")
    print("=" * 50)

    # 1. Testar APIs com detalhes de erro
    print("\n1. 🐛 DIAGNÓSTICO DE APIS:")
    apis_com_erro = [
        "/api/prestadores",
        "/api/servicos",
        "/api/categorias",
        "/api/estatisticas",
        "/api/busca"
    ]

    for api in apis_com_erro:
        try:
            response = requests.get(f"{BASE_URL}{api}")
            print(f"\n📡 {api}:")
            print(f"   Status: {response.status_code}")

            if response.status_code == 500:
                # Tentar obter detalhes do erro
                try:
                    erro_data = response.json()
                    print(f"   Erro: {erro_data.get('error', 'Erro desconhecido')}")
                except:
                    print(f"   Erro: {response.text[:200]}...")
            elif response.status_code == 400:
                print(f"   Bad Request - Parâmetros faltando")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # 2. Testar cadastro com dados específicos
    print("\n2. 👥 TESTE DE CADASTRO DETALHADO:")
    test_cadastro_detalhado()

    # 3. Verificar banco de dados
    print("\n3. 🗄️ VERIFICAÇÃO DE DADOS:")
    verificar_dados()

    print("\n🎯 RECOMENDAÇÕES:")
    print("• Executar: python tests/criar_dados_teste.py")
    print("• Verificar logs do servidor para erros 500")
    print("• Testar manualmente o cadastro")


def test_cadastro_detalhado():
    """Testar cadastro com diferentes abordagens"""
    test_cases = [
        {
            "nome": "Cliente Teste",
            "email": f"cliente_teste_{requests.utils.quote('teste@teste.com')}",
            "senha": "123456",
            "confirmar_senha": "123456",
            "tipo": "cliente"
        },
        {
            "nome": "Prestador Teste",
            "email": f"prestador_teste_{requests.utils.quote('teste@teste.com')}",
            "senha": "123456",
            "confirmar_senha": "123456",
            "tipo": "prestador",
            "categoria": "medico",
            "especialidade": "Clinico Geral",
            "descricao": "Teste",
            "experiencia": "5",
            "valor_hora": "1000"
        }
    ]

    for i, data in enumerate(test_cases):
        try:
            print(f"\n   📝 Tentativa {i + 1}: {data['tipo']}")
            response = requests.post(f"{BASE_URL}/auth/registro", data=data, allow_redirects=False)
            print(f"      Status: {response.status_code}")
            print(f"      Headers: {dict(response.headers)}")

            if response.status_code == 302:
                print(f"      ✅ Redirecionamento - Possível sucesso")
            else:
                print(f"      ❌ Falha - Verificar formulário")

        except Exception as e:
            print(f"      ❌ Exception: {e}")


def verificar_dados():
    """Verificar se há dados no banco"""
    try:
        # Verificar prestadores
        response = requests.get(f"{BASE_URL}/api/prestadores")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prestadores = data.get('data', [])
                print(f"   📊 Prestadores no BD: {len(prestadores)}")
            else:
                print(f"   ❌ API Prestadores: {data.get('error')}")
        else:
            print(f"   ❌ Não foi possível verificar prestadores")

        # Verificar serviços
        response = requests.get(f"{BASE_URL}/api/servicos")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                servicos = data.get('data', [])
                print(f"   📊 Serviços no BD: {len(servicos)}")

    except Exception as e:
        print(f"   ❌ Erro na verificação: {e}")


if __name__ == "__main__":
    diagnostico_completo()