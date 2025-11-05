# blueprints/agendamentos.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from database import db_session
from models import Agendamento, Servico, PrestadorServico, Notificacao, Conversa

agendamentos_bp = Blueprint('agendamentos', __name__, url_prefix='/agendamentos')


# Funções auxiliares para notificações
def criar_notificacao_agendamento(agendamento, tipo, titulo, mensagem, link_acao=None):
    """Função auxiliar para criar notificações"""
    try:
        usuario_id = agendamento.cliente_id if tipo == 'cliente' else agendamento.prestador.usuario_id
        notificacao = Notificacao(
            usuario_id=usuario_id,
            tipo='agendamento',
            titulo=titulo,
            mensagem=mensagem,
            link_acao=link_acao or f'/agendamentos/{agendamento.id}',
            data_criacao=datetime.now()
        )
        db_session.add(notificacao)
        return True
    except Exception as e:
        print(f"Erro ao criar notificação: {e}")
        return False


def notificar_confirmacao_agendamento(agendamento):
    """Notificar cliente sobre confirmação"""
    mensagem = f'{agendamento.prestador.usuario.nome} confirmou seu agendamento para {agendamento.data_agendamento.strftime("%d/%m/%Y às %H:%M")}'
    return criar_notificacao_agendamento(
        agendamento=agendamento,
        tipo='cliente',
        titulo='Agendamento Confirmado',
        mensagem=mensagem
    )


def notificar_recusa_agendamento(agendamento, motivo):
    """Notificar cliente sobre recusa"""
    mensagem = f'{agendamento.prestador.usuario.nome} recusou seu agendamento'
    if motivo:
        mensagem += f'. Motivo: {motivo}'
    return criar_notificacao_agendamento(
        agendamento=agendamento,
        tipo='cliente',
        titulo='Agendamento Recusado',
        mensagem=mensagem,
        link_acao='/servicos/buscar'
    )


def notificar_cancelamento_cliente(agendamento, motivo):
    """Notificar prestador sobre cancelamento do cliente"""
    mensagem = f'{agendamento.cliente.nome} cancelou o agendamento para {agendamento.data_agendamento.strftime("%d/%m/%Y às %H:%M")}'
    if motivo:
        mensagem += f'. Motivo: {motivo}'
    return criar_notificacao_agendamento(
        agendamento=agendamento,
        tipo='prestador',
        titulo='Agendamento Cancelado',
        mensagem=mensagem,
        link_acao='/agendamentos/prestador'
    )


def notificar_conclusao_servico(agendamento):
    """Notificar cliente sobre conclusão do serviço"""
    mensagem = f'O serviço "{agendamento.servico.titulo}" foi concluído por {agendamento.prestador.usuario.nome}. Por favor, avalie a experiência.'
    return criar_notificacao_agendamento(
        agendamento=agendamento,
        tipo='cliente',
        titulo='Serviço Concluído',
        mensagem=mensagem,
        link_acao=f'/agendamentos/{agendamento.id}/avaliar'
    )


@agendamentos_bp.route('/agendar/<int:servico_id>', methods=['GET', 'POST'])
@login_required
def agendar(servico_id):
    """Agendar serviço"""
    servico = db_session.query(Servico).get(servico_id)

    if not servico:
        flash('Serviço não encontrado.', 'warning')
        return redirect(url_for('servicos.buscar'))

    if request.method == 'POST':
        data_agendamento_str = request.form.get('data_agendamento')
        observacoes = request.form.get('observacoes', '')
        modalidade = request.form.get('modalidade', 'presencial')
        endereco_servico = request.form.get('endereco_servico', '')

        try:
            data_agendamento = datetime.strptime(data_agendamento_str, '%Y-%m-%dT%H:%M')

            # Verificar se a data não é no passado
            if data_agendamento < datetime.now():
                flash('Não é possível agendar para datas passadas.', 'warning')
                return render_template('agendamentos/agendar.html', servico=servico)

        except ValueError:
            flash('Selecione uma data e hora válidas.', 'warning')
            return render_template('agendamentos/agendar.html', servico=servico)

        # Verificar conflitos de horário para o prestador
        conflito = db_session.query(Agendamento).filter(
            Agendamento.prestador_id == servico.prestador_id,
            Agendamento.data_agendamento == data_agendamento,
            Agendamento.status.in_(['pendente', 'confirmado', 'em_andamento'])
        ).first()

        if conflito:
            flash('Este horário já está ocupado para o prestador. Por favor, escolha outro horário.', 'warning')
            return render_template('agendamentos/agendar.html', servico=servico)

        agendamento = Agendamento(
            cliente_id=current_user.id,
            prestador_id=servico.prestador_id,
            servico_id=servico.id,
            data_agendamento=data_agendamento,
            observacoes=observacoes,
            status='pendente',
            modalidade=modalidade,
            endereco_servico=endereco_servico if modalidade == 'presencial' else ''
        )

        db_session.add(agendamento)
        db_session.commit()

        # Criar notificação para o prestador usando a nova função
        notificar_novo_agendamento(agendamento)

        flash('Agendamento realizado com sucesso! Aguarde a confirmação do prestador.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('agendamentos/agendar.html', servico=servico)


def notificar_novo_agendamento(agendamento):
    """Notificar prestador sobre novo agendamento"""
    mensagem = f'{agendamento.cliente.nome} agendou seu serviço "{agendamento.servico.titulo}" para {agendamento.data_agendamento.strftime("%d/%m/%Y às %H:%M")}'
    return criar_notificacao_agendamento(
        agendamento=agendamento,
        tipo='prestador',
        titulo='Novo Agendamento',
        mensagem=mensagem
    )


@agendamentos_bp.route('/<int:agendamento_id>')
@login_required
def detalhes(agendamento_id):
    """Detalhes do agendamento"""
    agendamento = db_session.query(Agendamento).get(agendamento_id)

    if not agendamento:
        flash('Agendamento não encontrado.', 'warning')
        return redirect(url_for('main.dashboard'))

    # Verificar permissão
    if current_user.tipo == 'cliente' and agendamento.cliente_id != current_user.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    if current_user.tipo == 'prestador' and agendamento.prestador_id != current_user.prestador.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    return render_template('agendamentos/detalhes.html', agendamento=agendamento)


@agendamentos_bp.route('/<int:agendamento_id>/confirmar', methods=['POST'])
@login_required
def confirmar(agendamento_id):
    """Confirmar agendamento (prestador)"""
    agendamento = db_session.query(Agendamento).get(agendamento_id)

    if not agendamento or current_user.tipo != 'prestador' or agendamento.prestador_id != current_user.prestador.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    # Verificar se ainda está pendente
    if agendamento.status != 'pendente':
        flash('Este agendamento já foi processado.', 'warning')
        return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))

    agendamento.status = 'confirmado'
    agendamento.atualizado_em = datetime.now()

    # Criar notificação para o cliente usando a nova função
    notificar_confirmacao_agendamento(agendamento)

    try:
        db_session.commit()
        flash('Agendamento confirmado com sucesso!', 'success')
    except Exception as e:
        db_session.rollback()
        flash('Erro ao confirmar agendamento.', 'error')

    return redirect(url_for('agendamentos.agendamentos_prestador'))


@agendamentos_bp.route('/<int:agendamento_id>/recusar', methods=['POST'])
@login_required
def recusar(agendamento_id):
    """Recusar agendamento (prestador)"""
    agendamento = db_session.query(Agendamento).get(agendamento_id)

    if not agendamento or current_user.tipo != 'prestador' or agendamento.prestador_id != current_user.prestador.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    motivo = request.form.get('motivo', '')
    agendamento.status = 'cancelado'
    agendamento.observacoes = f"Cancelado pelo prestador: {motivo}" if motivo else "Cancelado pelo prestador"
    agendamento.atualizado_em = datetime.now()

    # Criar notificação para o cliente usando a nova função
    notificar_recusa_agendamento(agendamento, motivo)

    db_session.commit()

    flash('Agendamento recusado.', 'info')
    return redirect(url_for('agendamentos.agendamentos_prestador'))


@agendamentos_bp.route('/<int:agendamento_id>/cancelar', methods=['POST'])
@login_required
def cancelar(agendamento_id):
    """Cancelar agendamento (cliente)"""
    agendamento = db_session.query(Agendamento).get(agendamento_id)

    if not agendamento or current_user.tipo != 'cliente' or agendamento.cliente_id != current_user.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    motivo = request.form.get('motivo', '')
    agendamento.status = 'cancelado'
    agendamento.observacoes = f"Cancelado pelo cliente: {motivo}" if motivo else "Cancelado pelo cliente"
    agendamento.atualizado_em = datetime.now()

    # Criar notificação para o prestador usando a nova função
    notificar_cancelamento_cliente(agendamento, motivo)

    db_session.commit()

    flash('Agendamento cancelado.', 'info')
    return redirect(url_for('main.dashboard'))


@agendamentos_bp.route('/<int:agendamento_id>/concluir', methods=['POST'])
@login_required
def concluir(agendamento_id):
    """Concluir agendamento (prestador)"""
    agendamento = db_session.query(Agendamento).get(agendamento_id)

    if not agendamento or current_user.tipo != 'prestador' or agendamento.prestador_id != current_user.prestador.id:
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    agendamento.status = 'realizado'
    agendamento.atualizado_em = datetime.now()

    # Criar notificação para o cliente usando a nova função
    notificar_conclusao_servico(agendamento)

    db_session.commit()

    flash('Serviço marcado como concluído!', 'success')
    return redirect(url_for('agendamentos.detalhes', agendamento_id=agendamento_id))


@agendamentos_bp.route('/api/disponibilidade/<int:prestador_id>')
@login_required
def disponibilidade(prestador_id):
    """API: Verificar disponibilidade do prestador"""
    data_str = request.args.get('data')

    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else datetime.now().date()
    except ValueError:
        return jsonify({'error': 'Data inválida'}), 400

    # Buscar agendamentos do prestador para a data
    agendamentos = db_session.query(Agendamento).filter(
        Agendamento.prestador_id == prestador_id,
        db_session.func.date(Agendamento.data_agendamento) == data,
        Agendamento.status.in_(['pendente', 'confirmado', 'em_andamento'])
    ).all()

    horarios_ocupados = [ag.data_agendamento.strftime('%H:%M') for ag in agendamentos]

    # Gerar horários disponíveis (das 8h às 18h, intervalos de 1 hora)
    horarios_disponiveis = []
    for hora in range(8, 18):
        horario_str = f"{hora:02d}:00"
        if horario_str not in horarios_ocupados:
            horarios_disponiveis.append(horario_str)

    return jsonify({
        'data': data.strftime('%Y-%m-%d'),
        'horarios_ocupados': horarios_ocupados,
        'horarios_disponiveis': horarios_disponiveis
    })


@agendamentos_bp.route('/prestador')
@login_required
def agendamentos_prestador():
    """Página completa de agendamentos para prestadores"""
    if current_user.tipo != 'prestador':
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    # Filtros
    status = request.args.get('status', 'todos')
    busca = request.args.get('busca', '')
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10

    # Query base
    agendamentos_query = db_session.query(Agendamento).filter_by(
        prestador_id=current_user.prestador.id
    )

    # Aplicar filtros
    if status and status != 'todos':
        agendamentos_query = agendamentos_query.filter_by(status=status)

    if busca:
        agendamentos_query = agendamentos_query.join(Servico).filter(
            db_session.or_(
                Servico.titulo.ilike(f'%{busca}%'),
                Servico.descricao.ilike(f'%{busca}%')
            )
        )

    # Paginação manual - CORRIGIDA
    total_agendamentos = agendamentos_query.count()
    total_paginas = (total_agendamentos + por_pagina - 1) // por_pagina if total_agendamentos > 0 else 1

    offset = (pagina - 1) * por_pagina

    # Aplicar paginação
    agendamentos = agendamentos_query.order_by(
        Agendamento.data_agendamento.desc()
    ).offset(offset).limit(por_pagina).all()

    # Estatísticas
    stats = {
        'total': db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id).count(),
        'pendentes': db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id,
                                                             status='pendente').count(),
        'confirmados': db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id,
                                                               status='confirmado').count(),
        'realizados': db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id,
                                                              status='realizado').count(),
        'cancelados': db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id,
                                                              status='cancelado').count(),
    }

    # Objeto de paginação simulado
    paginacao = type('Pagina', (), {
        'page': pagina,
        'per_page': por_pagina,
        'total': total_agendamentos,
        'pages': total_paginas,
        'has_prev': pagina > 1,
        'has_next': pagina < total_paginas,
        'prev_num': pagina - 1,
        'next_num': pagina + 1,
        'iter_pages': lambda: range(1, total_paginas + 1) if total_paginas > 0 else [1]
    })()

    return render_template(
        'agendamentos/prestador.html',
        agendamentos=agendamentos,
        paginacao=paginacao,
        stats=stats,
        filtro_status=status,
        filtro_busca=busca
    )


@agendamentos_bp.route('/prestador/calendario')
@login_required
def calendario_prestador():
    """Visualização em calendário para prestadores"""
    if current_user.tipo != 'prestador':
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    agendamentos = db_session.query(Agendamento).filter_by(
        prestador_id=current_user.prestador.id
    ).filter(
        Agendamento.status.in_(['pendente', 'confirmado', 'em_andamento'])
    ).all()

    eventos_calendario = []
    for ag in agendamentos:
        eventos_calendario.append({
            'id': ag.id,
            'title': f"{ag.servico.titulo} - {ag.cliente.nome}",
            'start': ag.data_agendamento.isoformat() if ag.data_agendamento else None,
            'end': (ag.data_agendamento + timedelta(
                minutes=ag.servico.duracao)).isoformat() if ag.data_agendamento else None,
            'className': f'cal-{ag.status}',
            'extendedProps': {
                'status': ag.status,
                'cliente': ag.cliente.nome,
                'servico': ag.servico.titulo,
                'modalidade': ag.modalidade
            }
        })

    return render_template('agendamentos/calendario.html', eventos=eventos_calendario)


@agendamentos_bp.route('/prestador/exportar')
@login_required
def exportar_agendamentos():
    """Exportar agendamentos para CSV/Excel"""
    if current_user.tipo != 'prestador':
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    flash('Funcionalidade de exportação em desenvolvimento.', 'info')
    return redirect(url_for('agendamentos.agendamentos_prestador'))


@agendamentos_bp.route('/cliente')
@login_required
def agendamentos_cliente():
    """Página completa de agendamentos para clientes"""
    if current_user.tipo != 'cliente':
        flash('Acesso não autorizado.', 'warning')
        return redirect(url_for('main.dashboard'))

    # Filtros
    status = request.args.get('status', 'todos')
    busca = request.args.get('busca', '')

    # Query base
    agendamentos_query = db_session.query(Agendamento).filter_by(cliente_id=current_user.id)

    # Aplicar filtros
    if status and status != 'todos':
        agendamentos_query = agendamentos_query.filter_by(status=status)

    if busca:
        agendamentos_query = agendamentos_query.join(Servico).filter(
            db_session.or_(
                Servico.titulo.ilike(f'%{busca}%'),
                Servico.descricao.ilike(f'%{busca}%')
            )
        )

    agendamentos = agendamentos_query.order_by(Agendamento.data_agendamento.desc()).all()

    return render_template(
        'agendamentos/cliente.html',
        agendamentos=agendamentos,
        filtro_status=status,
        filtro_busca=busca
    )


@agendamentos_bp.route('/api/meus-agendamentos')
@login_required
def meus_agendamentos():
    """API: Listar agendamentos do usuário"""
    try:
        if current_user.tipo == 'cliente':
            agendamentos = db_session.query(Agendamento).filter_by(cliente_id=current_user.id)
        else:
            agendamentos = db_session.query(Agendamento).filter_by(prestador_id=current_user.prestador.id)

        status = request.args.get('status')
        if status:
            agendamentos = agendamentos.filter_by(status=status)

        agendamentos = agendamentos.order_by(Agendamento.data_agendamento.desc()).all()

        dados_agendamentos = []
        for ag in agendamentos:
            dados_agendamentos.append({
                'id': ag.id,
                'servico_titulo': ag.servico.titulo,
                'prestador_nome': ag.prestador.usuario.nome if current_user.tipo == 'cliente' else ag.cliente.nome,
                'data_agendamento': ag.data_agendamento.isoformat() if ag.data_agendamento else None,
                'status': ag.status,
                'modalidade': ag.modalidade,
                'valor': float(ag.servico.preco)
            })

        return jsonify({
            'success': True,
            'agendamentos': dados_agendamentos,
            'total': len(dados_agendamentos)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500