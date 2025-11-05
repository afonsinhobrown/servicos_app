from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request  # ✅
from flask_login import login_required, current_user
from database import db_session
from models import Usuario, PrestadorServico, Servico, Agendamento, TicketSuporte, Pagamento
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def check_admin():
    """Verificar se o usuário é administrador"""
    if current_user.tipo != 'admin':
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('main.dashboard'))


@admin_bp.route('/')
def dashboard():
    """Dashboard principal do administrador"""
    # Estatísticas básicas
    stats = {
        'total_usuarios': db_session.query(Usuario).count(),
        'total_prestadores': db_session.query(PrestadorServico).count(),
        'total_servicos': db_session.query(Servico).count(),
        'total_agendamentos': db_session.query(Agendamento).count(),
        'agendamentos_hoje': db_session.query(Agendamento).filter(
            func.date(Agendamento.data_agendamento) == datetime.today().date()
        ).count(),
        'tickets_abertos': db_session.query(TicketSuporte).filter_by(status='aberto').count(),
        'faturamento_mes': calcular_faturamento_mes(),
        'crescimento_usuarios': calcular_crescimento_usuarios()
    }

    # Dados para gráficos
    agendamentos_ultima_semana = agendamentos_por_periodo(7)
    usuarios_ultimo_mes = usuarios_por_periodo(30)

    # Tickets urgentes
    tickets_urgentes = db_session.query(TicketSuporte).filter_by(
        prioridade='urgente',
        status='aberto'
    ).order_by(TicketSuporte.data_abertura.desc()).limit(5).all()

    # Últimos agendamentos
    ultimos_agendamentos = db_session.query(Agendamento).order_by(
        Agendamento.criado_em.desc()
    ).limit(5).all()

    # Novos prestadores
    novos_prestadores = db_session.query(PrestadorServico).order_by(
        PrestadorServico.id.desc()
    ).limit(5).all()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           agendamentos_ultima_semana=agendamentos_ultima_semana,
                           usuarios_ultimo_mes=usuarios_ultimo_mes,
                           tickets_urgentes=tickets_urgentes,
                           ultimos_agendamentos=ultimos_agendamentos,
                           novos_prestadores=novos_prestadores)


@admin_bp.route('/meu-perfil')
def meu_perfil():
    """Página de perfil do administrador"""
    try:
        # Estatísticas pessoais do admin
        stats_admin = {
            'tickets_resolvidos': db_session.query(TicketSuporte).filter_by(
                status='fechado'
            ).count(),
            'tickets_em_aberto': db_session.query(TicketSuporte).filter_by(
                status='aberto'
            ).count(),
            'usuarios_ativos': db_session.query(Usuario).filter_by(ativo=True).count(),
            'prestadores_ativos': db_session.query(PrestadorServico).filter_by(
                disponivel='sim'
            ).count(),
        }

        # Últimas atividades
        ultimos_tickets = db_session.query(TicketSuporte).order_by(
            TicketSuporte.data_abertura.desc()
        ).limit(5).all()

        return render_template('admin/meu_perfil.html',
                               user=current_user,
                               stats=stats_admin,
                               ultimos_tickets=ultimos_tickets)

    except Exception as e:
        flash(f'Erro ao carregar perfil: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/api/estatisticas')
def estatisticas_api():
    """API para estatísticas em tempo real"""
    try:
        stats = {
            'total_usuarios': db_session.query(Usuario).count(),
            'total_prestadores': db_session.query(PrestadorServico).count(),
            'total_servicos': db_session.query(Servico).count(),
            'agendamentos_hoje': db_session.query(Agendamento).filter(
                func.date(Agendamento.data_agendamento) == datetime.today().date()
            ).count(),
            'tickets_abertos': db_session.query(TicketSuporte).filter_by(status='aberto').count(),
            'tickets_urgentes': db_session.query(TicketSuporte).filter_by(
                prioridade='urgente', status='aberto'
            ).count(),
        }

        return jsonify({'success': True, 'estatisticas': stats})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/agendamentos-semana')
def agendamentos_semana_api():
    """API para dados de agendamentos da semana"""
    try:
        dados = agendamentos_por_periodo(7)
        return jsonify({'success': True, 'dados': dados})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Funções auxiliares
def calcular_faturamento_mes():
    """Calcular faturamento do mês atual"""
    try:
        primeiro_dia_mes = datetime.today().replace(day=1)
        faturamento = db_session.query(func.sum(Pagamento.valor_total)).filter(
            Pagamento.status == 'pago',
            Pagamento.data_pagamento >= primeiro_dia_mes
        ).scalar()
        return float(faturamento) if faturamento else 0.0
    except:
        return 0.0


def calcular_crescimento_usuarios():
    """Calcular crescimento de usuários no último mês"""
    try:
        hoje = datetime.today()
        mes_passado = hoje - timedelta(days=30)

        usuarios_atuais = db_session.query(Usuario).count()
        usuarios_mes_passado = db_session.query(Usuario).filter(
            Usuario.data_cadastro < mes_passado
        ).count()

        if usuarios_mes_passado > 0:
            crescimento = ((usuarios_atuais - usuarios_mes_passado) / usuarios_mes_passado) * 100
            return round(crescimento, 1)
        return 0.0
    except:
        return 0.0


def agendamentos_por_periodo(dias):
    """Agendamentos dos últimos N dias"""
    try:
        data_inicio = datetime.today() - timedelta(days=dias)

        resultados = db_session.query(
            func.date(Agendamento.data_agendamento).label('data'),
            func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data_agendamento >= data_inicio
        ).group_by(
            func.date(Agendamento.data_agendamento)
        ).order_by('data').all()

        # Formatar dados para chart.js
        datas = []
        totais = []

        for i in range(dias):
            data = (datetime.today() - timedelta(days=i)).strftime('%d/%m')
            datas.append(data)

            # Encontrar total para esta data
            total = 0
            for resultado in resultados:
                if resultado.data.strftime('%d/%m') == data:
                    total = resultado.total
                    break
            totais.append(total)

        return {
            'labels': list(reversed(datas)),
            'data': list(reversed(totais))
        }
    except Exception as e:
        print(f"Erro em agendamentos_por_periodo: {e}")
        return {'labels': [], 'data': []}


def usuarios_por_periodo(dias):
    """Novos usuários dos últimos N dias"""
    try:
        data_inicio = datetime.today() - timedelta(days=dias)

        resultados = db_session.query(
            func.date(Usuario.data_cadastro).label('data'),
            func.count(Usuario.id).label('total')
        ).filter(
            Usuario.data_cadastro >= data_inicio
        ).group_by(
            func.date(Usuario.data_cadastro)
        ).order_by('data').all()

        # Formatar dados
        datas = []
        totais = []

        for i in range(dias):
            data = (datetime.today() - timedelta(days=i)).strftime('%d/%m')
            datas.append(data)

            total = 0
            for resultado in resultados:
                if resultado.data.strftime('%d/%m') == data:
                    total = resultado.total
                    break
            totais.append(total)

        return {
            'labels': list(reversed(datas)),
            'data': list(reversed(totais))
        }
    except Exception as e:
        print(f"Erro em usuarios_por_periodo: {e}")
        return {'labels': [], 'data': []}

@admin_bp.route('/meu-perfil/editar', methods=['GET', 'POST'])
def editar_perfil():
    """Editar perfil do administrador"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            telefone = request.form.get('telefone', '').strip()
            cidade = request.form.get('cidade', '').strip()
            bairro = request.form.get('bairro', '').strip()

            # Atualizar dados do usuário
            current_user.nome = nome
            current_user.telefone = telefone
            current_user.cidade = cidade
            current_user.bairro = bairro

            db_session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            return redirect(url_for('admin.meu_perfil'))

        except Exception as e:
            db_session.rollback()
            flash(f'Erro ao atualizar perfil: {str(e)}', 'error')

    return render_template('admin/editar_perfil.html', user=current_user)


@admin_bp.route('/meu-perfil/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    """Alterar senha do administrador"""
    if request.method == 'POST':
        try:
            senha_atual = request.form.get('senha_atual', '')
            nova_senha = request.form.get('nova_senha', '')
            confirmar_senha = request.form.get('confirmar_senha', '')

            # Validar senha atual
            if not current_user.check_senha(senha_atual):
                flash('Senha atual incorreta.', 'error')
                return render_template('admin/alterar_senha.html')

            # Validar nova senha
            if nova_senha != confirmar_senha:
                flash('As novas senhas não coincidem.', 'error')
                return render_template('admin/alterar_senha.html')

            if len(nova_senha) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('admin/alterar_senha.html')

            # Alterar senha
            current_user.set_senha(nova_senha)
            db_session.commit()

            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('admin.meu_perfil'))

        except Exception as e:
            db_session.rollback()
            flash(f'Erro ao alterar senha: {str(e)}', 'error')

    return render_template('admin/alterar_senha.html')

@admin_bp.route('/criar-usuario', methods=['GET', 'POST'])
def criar_usuario():
    """Criar novo usuário (admin, prestador ou cliente)"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            tipo = request.form.get('tipo', 'cliente')
            telefone = request.form.get('telefone', '').strip()
            cidade = request.form.get('cidade', '').strip()
            bairro = request.form.get('bairro', '').strip()

            # Validações
            if not all([nome, email, senha]):
                flash('Por favor, preencha todos os campos obrigatórios.', 'error')
                return render_template('admin/criar_usuario.html')

            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres.', 'error')
                return render_template('admin/criar_usuario.html')

            # Verificar se email já existe
            usuario_existente = db_session.query(Usuario).filter_by(email=email).first()
            if usuario_existente:
                flash('Este email já está cadastrado.', 'error')
                return render_template('admin/criar_usuario.html')

            # Criar usuário
            usuario = Usuario(
                nome=nome,
                email=email,
                tipo=tipo,
                telefone=telefone,
                cidade=cidade,
                bairro=bairro,
                data_cadastro=datetime.utcnow(),
                ativo=True
            )
            usuario.set_senha(senha)

            db_session.add(usuario)
            db_session.commit()

            # Se for prestador, criar registro na tabela prestadores_servico
            if tipo == 'prestador':
                prestador = PrestadorServico(
                    usuario_id=usuario.id,
                    categoria=request.form.get('categoria', 'outros'),
                    especialidade=request.form.get('especialidade', ''),
                    disponivel='sim',
                    verificado=True
                )
                db_session.add(prestador)
                db_session.commit()

            flash(f'Usuário {nome} criado com sucesso!', 'success')
            return redirect(url_for('admin.criar_usuario'))

        except Exception as e:
            db_session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'error')

    return render_template('admin/criar_usuario.html')