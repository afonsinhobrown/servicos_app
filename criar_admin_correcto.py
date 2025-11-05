# criar_admin_correto.py
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_session, engine
from models import Usuario, Base


def criar_admin_correto():
    """Cria apenas usuário admin, sem registro de prestador"""
    try:
        print("🔄 Iniciando criação do usuário administrador...")

        # Criar tabelas se não existirem
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas verificadas/criadas")

        # Verificar se já existe admin com este email
        admin_existente = db_session.query(Usuario).filter_by(email='admin@servicospro.mz').first()

        if admin_existente:
            print(f"📧 Usuário encontrado: {admin_existente.email}")

            # Verificar e atualizar tipo se necessário
            if admin_existente.tipo != 'admin':
                print(f"🔄 Atualizando tipo de '{admin_existente.tipo}' para 'admin'...")
                admin_existente.tipo = 'admin'
                db_session.commit()
                print("✅ Tipo atualizado para admin!")
            else:
                print("✅ Usuário já é admin!")

            print(f"👤 Dados do admin:")
            print(f"   Nome: {admin_existente.nome}")
            print(f"   Email: {admin_existente.email}")
            print(f"   Tipo: {admin_existente.tipo}")
            print(f"   ID: {admin_existente.id}")
            return

        # Criar NOVO usuário admin
        print("👤 Criando novo usuário administrador...")

        admin = Usuario(
            nome="Administrador Principal",
            email="admin@servicospro.mz",
            tipo="admin",  # IMPORTANTE: tipo admin
            telefone="+258841234567",
            cidade="Maputo",
            bairro="Centro",
            data_cadastro=datetime.utcnow(),
            ativo=True
        )

        # Definir senha
        admin.set_senha("admin123")

        db_session.add(admin)
        db_session.commit()

        print("🎉 ADMIN CRIADO COM SUCESSO!")
        print("═" * 50)
        print(f"📧 Email: admin@servicospro.mz")
        print(f"🔑 Senha: admin123")
        print(f"👤 Nome: Administrador Principal")
        print(f"📞 Telefone: +258841234567")
        print(f"🏙️ Cidade: Maputo")
        print(f"👥 Tipo: Administrador")
        print("═" * 50)
        print("💡 Este usuário acessará o DASHBOARD ADMIN")
        print("⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")

    except Exception as e:
        print(f"❌ ERRO AO CRIAR ADMIN: {str(e)}")
        print("🔍 Detalhes do erro:")
        import traceback
        traceback.print_exc()
        db_session.rollback()
    finally:
        db_session.close()
        print("\n🔒 Conexão com banco fechada.")


def verificar_admin():
    """Função para verificar se o admin foi criado corretamente"""
    try:
        print("\n" + "=" * 60)
        print("🔍 VERIFICANDO ADMIN NO BANCO DE DADOS...")
        print("=" * 60)

        # Buscar todos os usuários admin
        admins = db_session.query(Usuario).filter_by(tipo='admin').all()

        if not admins:
            print("❌ Nenhum usuário admin encontrado no banco!")
            return False

        print(f"✅ Encontrados {len(admins)} usuário(s) admin:")

        for admin in admins:
            print(f"\n👤 Admin #{admin.id}:")
            print(f"   Nome: {admin.nome}")
            print(f"   Email: {admin.email}")
            print(f"   Tipo: {admin.tipo}")
            print(f"   Ativo: {admin.ativo}")
            print(f"   Data Cadastro: {admin.data_cadastro}")

        return True

    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False
    finally:
        db_session.close()


if __name__ == "__main__":
    print("🚀 INICIANDO CRIAÇÃO DO USUÁRIO ADMINISTRADOR")
    print("=" * 60)

    # Criar admin
    criar_admin_correto()

    # Verificar criação
    verificar_admin()

    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python app.py")
    print("2. Acesse: http://localhost:5000/login")
    print("3. Login com: admin@servicospro.mz / admin123")
    print("4. Acesse: http://localhost:5000/dashboard")
    print("5. Deve redirecionar para o Dashboard Admin")
    print("=" * 60)