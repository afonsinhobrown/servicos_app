# criar_admin.py
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_session, engine
from models import Usuario, Base
from config import config


def criar_usuario_admin():
    """Cria um usuário administrador"""
    try:
        # Criar tabelas se não existirem
        Base.metadata.create_all(bind=engine)

        # Verificar se já existe um admin
        admin_existente = db_session.query(Usuario).filter_by(tipo='admin').first()
        if admin_existente:
            print(f"❌ Já existe um usuário admin: {admin_existente.email}")
            return

        # Criar usuário admin
        admin = Usuario(
            nome="Administrador Sistema",
            email="admin@servicospro.mz",
            tipo="admin",
            telefone="+258841234567",
            cidade="Maputo",
            bairro="Centro",
            ativo=True
        )
        admin.set_senha("admin123")  # Senha padrão - altere depois!

        db_session.add(admin)
        db_session.commit()

        print("✅ Usuário admin criado com sucesso!")
        print(f"📧 Email: admin@servicospro.mz")
        print(f"🔑 Senha: admin123")
        print("⚠️  ALTERE A SENHA APÓS O PRIMEIRO LOGIN!")

    except Exception as e:
        print(f"❌ Erro ao criar admin: {str(e)}")
        db_session.rollback()
    finally:
        db_session.close()


if __name__ == "__main__":
    criar_usuario_admin()