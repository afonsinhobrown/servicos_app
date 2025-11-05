# blueprints/main.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from database import db_session
from models import PrestadorServico, Servico, Usuario, Agendamento, CategoriaServico, Pagamento
from config import config
from datetime import datetime
from sqlalchemy import or_



main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial"""
    try:
        stats = {
            'total_prestadores': db_session.query(PrestadorServico).filter_by(disponivel='sim').count(),
            'destaques': db_session.query(PrestadorServico).filter_by(disponivel='sim').limit(6).all()
        }
        return render_template('index.html', stats=stats)
    except Exception as e:
        print(f"Erro na página inicial: {e}")
        return render_template('index.html', stats={})


@main_bp.route('/sobre')
def sobre():
    """Página sobre"""
    return render_template('static/sobre.html')


@main_bp.route('/contato')
def contato():
    """Página contato"""
    return render_template('static/contato.html')


# No seu blueprints/main.py - ADICIONE ESTA ROTA COMPLETA:

# No seu blueprints/main.py - ROTA CORRIGIDA:

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do usuário"""
    try:
        print(f"🔍 DEBUG: Iniciando dashboard para usuário {current_user.id} (tipo: {current_user.tipo})")

        # ✅ PRIMEIRO: Verificar se é ADMIN - redirecionar para dashboard admin
        if current_user.tipo == 'admin':
            print("👑 Redirecionando para dashboard admin...")
            return redirect(url_for('admin.dashboard'))

        # ✅ Cliente
        elif current_user.tipo == 'cliente':
            print("📋 Buscando agendamentos do cliente...")

            # Buscar agendamentos do cliente
            agendamentos = db_session.query(Agendamento).filter_by(
                cliente_id=current_user.id
            ).order_by(Agendamento.data_agendamento.desc()).all()

            print(f"✅ Encontrados {len(agendamentos)} agendamentos")

            # Garantir que todos os dados sejam seguros
            agendamentos_seguros = []
            for agendamento in agendamentos:
                try:
                    # Verificar se o serviço existe e tem preço
                    if agendamento.servico:
                        if agendamento.servico.preco is None:
                            agendamento.servico.preco = 0.0

                    # Verificar se o prestador existe
                    if not agendamento.prestador:
                        print(f"⚠️  Agendamento {agendamento.id} sem prestador, pulando...")
                        continue

                    agendamentos_seguros.append(agendamento)
                except Exception as e:
                    print(f"⚠️  Erro no agendamento {agendamento.id}: {e}")
                    continue

            # Estatísticas para cliente
            stats_cliente = {
                'total_agendamentos': len(agendamentos_seguros),
                'agendamentos_pendentes': len([a for a in agendamentos_seguros if a.status == 'pendente']),
                'agendamentos_confirmados': len([a for a in agendamentos_seguros if a.status == 'confirmado']),
                'agendamentos_concluidos': len([a for a in agendamentos_seguros if a.status == 'concluido']),
            }

            print("🚀 Renderizando template do dashboard do cliente...")
            return render_template('dashboard/cliente.html',
                                   user=current_user,
                                   agendamentos=agendamentos_seguros,
                                   stats=stats_cliente,
                                   now=datetime.now())

        # ✅ Prestador
        elif current_user.tipo == 'prestador':
            print("👨‍💼 Carregando dashboard do prestador...")

            # Buscar dados do prestador
            prestador = db_session.query(PrestadorServico).filter_by(
                usuario_id=current_user.id
            ).first()

            if not prestador:
                flash('Perfil de prestador não encontrado. Complete seu cadastro.', 'warning')
                return redirect(url_for('servicos.completar_perfil'))

            # Buscar serviços do prestador
            servicos = db_session.query(Servico).filter_by(
                prestador_id=prestador.id
            ).all()

            # Buscar agendamentos do prestador
            agendamentos = db_session.query(Agendamento).filter_by(
                prestador_id=prestador.id
            ).order_by(Agendamento.data_agendamento.desc()).all()

            # Calcular estatísticas do prestador
            stats_prestador = {
                'total_servicos': len(servicos),
                'total_agendamentos': len(agendamentos),
                'agendamentos_pendentes': len([a for a in agendamentos if a.status == 'pendente']),
                'agendamentos_confirmados': len([a for a in agendamentos if a.status == 'confirmado']),
                'agendamentos_concluidos': len([a for a in agendamentos if a.status == 'concluido']),
                'avaliacao_media': 4.8,  # Placeholder - implementar cálculo real
                'faturamento_mes': calcular_faturamento_prestador(prestador.id),
            }

            # Próximos agendamentos (após hoje)
            hoje = datetime.now().date()
            proximos_agendamentos = [
                a for a in agendamentos
                if a.data_agendamento.date() >= hoje
            ][:5]  # Últimos 5 agendamentos

            print("🚀 Renderizando template do dashboard do prestador...")
            return render_template('dashboard/prestador.html',
                                   prestador=prestador,
                                   servicos=servicos,
                                   agendamentos=proximos_agendamentos,
                                   stats=stats_prestador,
                                   now=datetime.now())

        # ❌ Tipo desconhecido
        else:
            print(f"❌ Tipo de usuário desconhecido: {current_user.tipo}")
            flash('Tipo de usuário não reconhecido.', 'error')
            return redirect(url_for('main.index'))

    except Exception as e:
        print(f"🔥 ERRO CRÍTICO NO DASHBOARD: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))


# Função auxiliar para calcular faturamento do prestador
def calcular_faturamento_prestador(prestador_id):
    """Calcular faturamento do mês atual para um prestador"""
    try:
        primeiro_dia_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Buscar pagamentos do prestador neste mês
        pagamentos = db_session.query(Pagamento).join(Agendamento).filter(
            Agendamento.prestador_id == prestador_id,
            Pagamento.status == 'pago',
            Pagamento.data_pagamento >= primeiro_dia_mes
        ).all()

        faturamento = sum(p.valor_prestador for p in pagamentos if p.valor_prestador)
        return float(faturamento) if faturamento else 0.0

    except Exception as e:
        print(f"Erro ao calcular faturamento: {e}")
        return 0.0


@main_bp.route('/criar-categorias')
def criar_categorias():
    """Criar categorias no banco"""
    try:
        categorias = [
            {'nome': 'Médico', 'slug': 'medico', 'icone': 'heart-pulse', 'ordem': 1},
            {'nome': 'Psicólogo', 'slug': 'psicologo', 'icone': 'brain', 'ordem': 2},
            {'nome': 'Personal Trainer', 'slug': 'personal_trainer', 'icone': 'activity', 'ordem': 3},
            {'nome': 'Cozinheiro', 'slug': 'cozinheiro', 'icone': 'egg-fried', 'ordem': 4},
            {'nome': 'Advogado', 'slug': 'advogado', 'icone': 'briefcase', 'ordem': 5},
            {'nome': 'Consultor', 'slug': 'consultor', 'icone': 'graph-up', 'ordem': 6},
        ]

        for cat_data in categorias:
            if not db_session.query(CategoriaServico).filter_by(slug=cat_data['slug']).first():
                categoria = CategoriaServico(**cat_data)
                db_session.add(categoria)

        db_session.commit()

        return '''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: green;">✅ Categorias Criadas!</h1>
            <p>Categorias criadas com sucesso.</p>
            <a href="/criar-prestadores-teste" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                👥 Criar Prestadores Teste
            </a>
        </div>
        '''
    except Exception as e:
        db_session.rollback()
        return f'''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: red;">❌ Erro: {str(e)}</h1>
            <a href="/">Voltar</a>
        </div>
        '''


@main_bp.route('/criar-prestadores-teste')
def criar_prestadores_teste():
    """Criar prestadores de teste"""
    try:
        # Dados de exemplo para MOÇAMBIQUE
        dados_mocambique = [
            ('medico', 'Clínico Geral', 'Consultas médicas gerais e acompanhamento de saúde', 8, 1500.0,
             'Dr. João Maputo'),
            ('psicologo', 'Aconselhamento', 'Apoio psicológico e orientação emocional', 6, 1200.0, 'Dra. Maria Matola'),
            ('personal_trainer', 'Fitness', 'Treino personalizado e orientação física', 4, 800.0, 'Coach Carlos'),
            ('cozinheiro', 'Culinária Local', 'Aulas de culinária tradicional moçambicana', 5, 1000.0, 'Chef Ana'),
            ('advogado', 'Direito Civil', 'Assessoria jurídica e consultoria legal', 10, 2000.0, 'Dr. José Silva'),
            ('consultor', 'Negócios', 'Consultoria empresarial e planeamento estratégico', 7, 1800.0,
             'Consultor Sérgio')
        ]

        for i, (categoria, especialidade, descricao, experiencia, valor_hora, nome) in enumerate(dados_mocambique):
            email = f'{categoria}{i}@servicos.co.mz'

            # Verificar se já existe
            usuario_existente = db_session.query(Usuario).filter_by(email=email).first()
            if not usuario_existente:
                usuario = Usuario(
                    nome=nome,
                    email=email,
                    tipo='prestador',
                    telefone='+258 84 000 0000',
                    cidade='Maputo',
                    bairro='Central'
                )
                usuario.set_senha('123456')
                db_session.add(usuario)
                db_session.commit()

                prestador = PrestadorServico(
                    usuario_id=usuario.id,
                    categoria=categoria,
                    especialidade=especialidade,
                    descricao=descricao,
                    experiencia=experiencia,
                    valor_hora=valor_hora,
                    disponivel='sim',
                    disponivel_online=True
                )
                db_session.add(prestador)
                db_session.commit()

                # Criar serviço
                servico = Servico(
                    prestador_id=prestador.id,
                    titulo=f'Serviço de {especialidade}',
                    descricao=descricao,
                    nivel='intermediario',
                    duracao=60,
                    preco=valor_hora
                )
                db_session.add(servico)

        db_session.commit()

        return '''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: green;">✅ Prestadores Criados!</h1>
            <p>Prestadores de serviço criados com sucesso!</p>
            <a href="/servicos/buscar" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                🔍 Ver Busca
            </a>
        </div>
        '''

    except Exception as e:
        db_session.rollback()
        return f'''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: red;">❌ Erro: {str(e)}</h1>
            <a href="/">Voltar</a>
        </div>
        '''


@main_bp.route('/debug-prestador/<int:prestador_id>')
def debug_prestador(prestador_id):
    """Debug: ver dados do prestador"""
    from database import db_session
    from models import PrestadorServico, Usuario

    prestador = db_session.query(PrestadorServico).get(prestador_id)

    if prestador:
        return f"""
        <h1>✅ Prestador {prestador_id} ENCONTRADO</h1>
        <p><strong>Nome:</strong> {prestador.usuario.nome}</p>
        <p><strong>Email:</strong> {prestador.usuario.email}</p>
        <p><strong>Especialidade:</strong> {prestador.especialidade}</p>
        <p><strong>Categoria:</strong> {prestador.categoria}</p>
        <a href="/servicos/prestador/{prestador_id}">Testar Perfil</a>
        """
    else:
        return f"<h1>❌ Prestador {prestador_id} NÃO ENCONTRADO</h1>"


@main_bp.route('/ver-prestadores')
def ver_prestadores():
    """Ver prestadores existentes no banco"""
    try:
        prestadores = db_session.query(PrestadorServico).all()

        if not prestadores:
            return '''
            <div style="padding: 20px; text-align: center;">
                <h1 style="color: orange;">📭 Nenhum Prestador Encontrado</h1>
                <p>Não há prestadores cadastrados no banco de dados.</p>
                <a href="/criar-prestadores-teste" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    👥 Criar Prestadores Teste
                </a>
            </div>
            '''

        html = f'''
        <div style="padding: 20px;">
            <h1>🎯 Prestadores no Banco: {len(prestadores)}</h1>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
        '''

        for prestador in prestadores:
            html += f'''
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px;">
                    <h3>👤 {prestador.usuario.nome}</h3>
                    <p><strong>Especialidade:</strong> {prestador.especialidade}</p>
                    <p><strong>Categoria:</strong> {prestador.categoria}</p>
                    <p><strong>Experiência:</strong> {prestador.experiencia} anos</p>
                    <p><strong>Preço:</strong> MZN {prestador.valor_hora}/h</p>
                    <p><strong>Disponível:</strong> {prestador.disponivel}</p>
                    <a href="/servicos/prestador/{prestador.id}" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">
                        Ver Perfil
                    </a>
                </div>
            '''

        html += '''
            </div>
            <div style="margin-top: 30px; text-align: center;">
                <a href="/servicos/buscar" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 18px;">
                    🔍 Testar Busca
                </a>
            </div>
        </div>
        '''

        return html

    except Exception as e:
        return f'<h1>❌ Erro: {str(e)}</h1>'


@main_bp.route('/perfil/<int:prestador_id>')
def perfil_alternativo(prestador_id):
    """Rota ALTERNATIVA para perfis - SEM problemas de roteamento"""
    try:
        from database import db_session
        from models import PrestadorServico, Servico

        prestador = db_session.query(PrestadorServico).get(prestador_id)

        if not prestador:
            return "Prestador não encontrado", 404

        servicos = db_session.query(Servico).filter_by(prestador_id=prestador_id).all()

        stats = {
            'total_servicos': len(servicos),
            'clientes_atendidos': len(servicos)
        }

        # Template SIMPLES e FUNCIONAL
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{prestador.usuario.nome} - ServiçosPro</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container">
                    <a class="navbar-brand" href="/">ServiçosPro</a>
                </div>
            </nav>

            <div class="container py-5">
                <div class="row">
                    <div class="col-12">
                        <h1 class="text-primary">{prestador.usuario.nome}</h1>
                        <p class="lead text-muted">{prestador.especialidade}</p>

                        <div class="row mt-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-body">
                                        <h5>Informações do Profissional</h5>
                                        <p><strong>Experiência:</strong> {prestador.experiencia} anos</p>
                                        <p><strong>Preço:</strong> MZN {prestador.valor_hora}/hora</p>
                                        <p><strong>Email:</strong> {prestador.usuario.email}</p>
                                        <p><strong>Total de Serviços:</strong> {len(servicos)}</p>
                                        <p><strong>Descrição:</strong> {prestador.descricao}</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="mt-4">
                            <a href="/servicos/buscar" class="btn btn-primary">Voltar para Busca</a>
                            <a href="/" class="btn btn-outline-secondary">Página Inicial</a>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Erro: {str(e)}", 500


@main_bp.route('/atualizar-banco')
def atualizar_banco():
    """Rota para atualizar o banco"""
    try:
        # Criar tabelas que não existem
        from models import Base
        Base.metadata.create_all(bind=db_session.bind)

        return '''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: green;">✅ Banco Atualizado!</h1>
            <p>As tabelas foram criadas/atualizadas com sucesso.</p>
            <a href="/criar-categorias" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                🏷️ Criar Categorias
            </a>
        </div>
        '''
    except Exception as e:
        return f'''
        <div style="padding: 20px; text-align: center;">
            <h1 style="color: red;">❌ Erro: {str(e)}</h1>
            <a href="/">Voltar</a>
        </div>
        '''


