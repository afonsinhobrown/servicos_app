from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import TicketSuporte, Notificacao, Usuario, TicketResposta
from datetime import datetime

admin_tickets_bp = Blueprint('admin_tickets', __name__, url_prefix='/admin/tickets')


@admin_tickets_bp.before_request
@login_required
def check_admin():
    """Verificar se o usuário é administrador"""
    if current_user.tipo != 'admin':
        flash('Acesso não autorizado.', 'error')
        return redirect(url_for('main.dashboard'))


@admin_tickets_bp.route('/')
def lista_tickets():
    """Lista todos os tickets para administração"""
    # Filtros
    status = request.args.get('status', 'todos')
    prioridade = request.args.get('prioridade', 'todos')
    categoria = request.args.get('categoria', 'todos')

    # Query base
    query = db_session.query(TicketSuporte).join(Usuario)

    # Aplicar filtros
    if status != 'todos':
        query = query.filter(TicketSuporte.status == status)
    if prioridade != 'todos':
        query = query.filter(TicketSuporte.prioridade == prioridade)
    if categoria != 'todos':
        query = query.filter(TicketSuporte.categoria == categoria)

    tickets = query.order_by(
        TicketSuporte.data_abertura.desc()
    ).all()

    # Estatísticas
    estatisticas = {
        'total': db_session.query(TicketSuporte).count(),
        'abertos': db_session.query(TicketSuporte).filter_by(status='aberto').count(),
        'em_andamento': db_session.query(TicketSuporte).filter_by(status='em_andamento').count(),
        'respondidos': db_session.query(TicketSuporte).filter_by(status='respondido').count(),
        'fechados': db_session.query(TicketSuporte).filter_by(status='fechado').count(),
    }

    return render_template('admin/tickets/lista_tickets.html',
                           tickets=tickets,
                           estatisticas=estatisticas,
                           filtros={'status': status, 'prioridade': prioridade, 'categoria': categoria})


@admin_tickets_bp.route('/<int:ticket_id>')
def detalhes_ticket(ticket_id):
    """Detalhes de um ticket específico"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            flash('Ticket não encontrado.', 'error')
            return redirect(url_for('admin_tickets.lista_tickets'))

        # Buscar respostas do ticket (CORRETO)
        respostas = db_session.query(TicketResposta).filter_by(
            ticket_id=ticket_id
        ).order_by(TicketResposta.data_resposta.asc()).all()

        return render_template('admin/tickets/detalhes_ticket.html',
                               ticket=ticket,
                               respostas=respostas)

    except Exception as e:
        flash(f'Erro ao carregar ticket: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.lista_tickets'))


@admin_tickets_bp.route('/<int:ticket_id>/responder', methods=['POST'])
def responder_ticket(ticket_id):
    """Admin responde a um ticket"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            flash('Ticket não encontrado.', 'error')
            return redirect(url_for('admin_tickets.lista_tickets'))

        resposta_texto = request.form.get('resposta', '').strip()
        acao = request.form.get('acao', 'responder')

        if not resposta_texto:
            flash('Por favor, escreva uma resposta.', 'warning')
            return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))

        print(f"DEBUG: Admin {current_user.id} respondendo ticket {ticket_id}")
        print(f"DEBUG: Texto da resposta: {resposta_texto}")

        # Criar registro da resposta
        nova_resposta = TicketResposta(
            ticket_id=ticket_id,
            usuario_id=current_user.id,  # ID do admin
            resposta=resposta_texto,
            data_resposta=datetime.utcnow()
        )
        db_session.add(nova_resposta)

        # Atualizar status baseado na ação
        if acao == 'resolver':
            ticket.status = 'respondido'
            ticket.data_resolucao = datetime.utcnow()
            ticket.resolucao = resposta_texto

        db_session.commit()

        print(f"DEBUG: Resposta salva com ID {nova_resposta.id}")

        flash('Resposta enviada com sucesso!', 'success')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))

    except Exception as e:
        db_session.rollback()
        print(f"ERRO ao responder ticket: {str(e)}")
        flash(f'Erro ao enviar resposta: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))



@admin_tickets_bp.route('/<int:ticket_id>/fechar', methods=['POST'])
def fechar_ticket(ticket_id):
    """Admin fecha um ticket"""
    ticket = db_session.query(TicketSuporte).get(ticket_id)

    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('admin_tickets.lista_tickets'))

    ticket.status = 'fechado'
    ticket.data_resolucao = datetime.utcnow()

    # Notificar o usuário
    notificacao = Notificacao(
        usuario_id=ticket.usuario_id,
        tipo='ticket',
        titulo='Ticket Fechado',
        mensagem=f'Seu ticket "{ticket.assunto}" foi fechado pela equipe',
        link_acao=f'/tickets/{ticket.id}'
    )
    db_session.add(notificacao)

    db_session.commit()

    flash('Ticket fechado com sucesso.', 'success')
    return redirect(url_for('admin_tickets.lista_tickets'))


@admin_tickets_bp.route('/<int:ticket_id>/prioridade', methods=['POST'])
def alterar_prioridade(ticket_id):
    """Alterar prioridade de um ticket"""
    ticket = db_session.query(TicketSuporte).get(ticket_id)

    if not ticket:
        return jsonify({'success': False, 'error': 'Ticket não encontrado'})

    nova_prioridade = request.json.get('prioridade')
    if nova_prioridade not in ['baixa', 'media', 'alta', 'urgente']:
        return jsonify({'success': False, 'error': 'Prioridade inválida'})

    ticket.prioridade = nova_prioridade
    db_session.commit()

    return jsonify({'success': True, 'nova_prioridade': nova_prioridade})


@admin_tickets_bp.route('/api/estatisticas')
def estatisticas_tickets():
    """API: Estatísticas para dashboard admin"""
    try:
        total_tickets = db_session.query(TicketSuporte).count()
        tickets_abertos = db_session.query(TicketSuporte).filter_by(status='aberto').count()
        tickets_em_andamento = db_session.query(TicketSuporte).filter_by(status='em_andamento').count()
        tickets_urgentes = db_session.query(TicketSuporte).filter_by(prioridade='urgente').count()

        # Tickets por categoria
        categorias = db_session.query(
            TicketSuporte.categoria,
            db_session.func.count(TicketSuporte.id)
        ).group_by(TicketSuporte.categoria).all()

        return jsonify({
            'success': True,
            'estatisticas': {
                'total_tickets': total_tickets,
                'tickets_abertos': tickets_abertos,
                'tickets_em_andamento': tickets_em_andamento,
                'tickets_urgentes': tickets_urgentes,
                'categorias': dict(categorias)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500