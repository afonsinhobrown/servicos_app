# tests/criar_dados_teste.py
import sys
import os
import random

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_session
from models import Usuario, PrestadorServico, Servico


def criar_dados_teste_realistas():
    """Criar dados de teste realistas para Moçambique"""

    categorias_especialidades = {
        'medico': ['Clínico Geral', 'Pediatra', 'Cardiologista', 'Dermatologista'],
        'psicologo': ['Aconselhamento', 'Terapia Familiar', 'Psicologia Clínica'],
        'personal_trainer': ['Fitness', 'Reabilitação', 'Condicionamento Físico'],
        'cozinheiro': ['Culinária Tradicional', 'Culinária Internacional', 'Doces e Sobremesas'],
        'advogado': ['Direito Civil', 'Direito Criminal', 'Direito Trabalhista'],
        'consultor': ['Negócios', 'TI', 'Marketing Digital']
    }

    nomes_mocambicanos = [
        'João Maputo', 'Maria Matola', 'Carlos Beira', 'Ana Nampula',
        'José Quelimane', 'Teresa Tete', 'Paulo Pemba', 'Luisa Inhambane',
        'Miguel Xai-Xai', 'Catarina Chimoio', 'António Lichinga', 'Isabel Maxixe'
    ]

    print("🔄 Criando dados de teste realistas...")

    try:
        # Criar prestadores de serviço
        for i, nome in enumerate(nomes_mocambicanos):
            categoria = random.choice(list(categorias_especialidades.keys()))
            especialidade = random.choice(categorias_especialidades[categoria])

            # Verificar se usuário já existe
            email = f"prestador{i}@servicos.co.mz"
            usuario_existente = db_session.query(Usuario).filter_by(email=email).first()

            if not usuario_existente:
                # Criar usuário
                usuario = Usuario(
                    nome=nome,
                    email=email,
                    tipo='prestador'
                )
                usuario.set_senha('123456')
                db_session.add(usuario)
                db_session.commit()

                # Criar prestador
                prestador = PrestadorServico(
                    usuario_id=usuario.id,
                    categoria=categoria,
                    especialidade=especialidade,
                    descricao=f"Profissional qualificado em {especialidade} com anos de experiência servindo a comunidade moçambicana.",
                    experiencia=random.randint(2, 15),
                    valor_hora=random.randint(500, 2500),
                    disponivel='sim',
                    taxa_plataforma=10.0
                )
                db_session.add(prestador)
                db_session.commit()

                # Criar serviços
                for j in range(random.randint(1, 3)):
                    servico = Servico(
                        prestador_id=prestador.id,
                        titulo=f"Serviço de {especialidade} - {['Básico', 'Intermediário', 'Avançado'][j]}",
                        descricao=f"Serviço profissional de {especialidade} com qualidade garantida. Atendimento personalizado para suas necessidades.",
                        nivel=['basico', 'intermediario', 'avancado'][j],
                        duracao=random.choice([30, 60, 90, 120]),
                        preco=prestador.valor_hora * (random.randint(1, 4)),
                        ativo=True
                    )
                    db_session.add(servico)

                db_session.commit()
                print(f"✅ Criado: {nome} - {especialidade}")

        print("🎉 Dados de teste criados com sucesso!")
        print("📊 Estatísticas:")
        print(f"   • Prestadores: {db_session.query(PrestadorServico).count()}")
        print(f"   • Serviços: {db_session.query(Servico).count()}")
        print(f"   • Usuários: {db_session.query(Usuario).count()}")

    except Exception as e:
        db_session.rollback()
        print(f"❌ Erro ao criar dados de teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    criar_dados_teste_realistas()