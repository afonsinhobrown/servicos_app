from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import TicketSuporte, Notificacao, Usuario, TicketResposta
from datetime import datetime
from sqlalchemy import or_

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
    """Lista de todos os tickets"""
    try:
        # Filtros
        status = request.args.get('status', 'todos')
        prioridade = request.args.get('prioridade', 'todos')
        pagina = request.args.get('pagina', 1, type=int)
        por_pagina = 20

        # Query base
        query = db_session.query(TicketSuporte)

        # Aplicar filtros
        if status != 'todos':
            query = query.filter(TicketSuporte.status == status)
        if prioridade != 'todos':
            query = query.filter(TicketSuporte.prioridade == prioridade)

        # Ordenação e paginação
        tickets = query.order_by(TicketSuporte.data_abertura.desc()).paginate(
            page=pagina, per_page=por_pagina, error_out=False
        )

        # Estatísticas
        estatisticas = {
            'total': db_session.query(TicketSuporte).count(),
            'abertos': db_session.query(TicketSuporte).filter_by(status='aberto').count(),
            'em_andamento': db_session.query(TicketSuporte).filter_by(status='em_andamento').count(),
            'respondidos': db_session.query(TicketSuporte).filter_by(status='respondido').count(),
            'fechados': db_session.query(TicketSuporte).filter_by(status='fechado').count(),
        }

        return render_template('admin/tickets/lista.html',
                               tickets=tickets,
                               estatisticas=estatisticas,
                               status=status,
                               prioridade=prioridade)

    except Exception as e:
        flash(f'Erro ao carregar tickets: {str(e)}', 'error')
        return render_template('admin/tickets/lista.html', tickets=[], estatisticas={})


@admin_tickets_bp.route('/<int:ticket_id>')
def detalhes_ticket(ticket_id):
    """Detalhes de um ticket específico"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            flash('Ticket não encontrado.', 'error')
            return redirect(url_for('admin_tickets.lista_tickets'))

        # Buscar respostas do ticket
        respostas = db_session.query(TicketResposta).filter_by(
            ticket_id=ticket_id
        ).order_by(TicketResposta.data_resposta.asc()).all()

        return render_template('admin/tickets/detalhes.html',
                               ticket=ticket,
                               respostas=respostas)

    except Exception as e:
        flash(f'Erro ao carregar ticket: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.lista_tickets'))


@admin_tickets_bp.route('/<int:ticket_id>/responder', methods=['POST'])
def responder_ticket(ticket_id):
    """Responder a um ticket como administrador"""
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

        # Criar registro da resposta
        nova_resposta = TicketResposta(
            ticket_id=ticket_id,
            usuario_id=current_user.id,
            resposta=resposta_texto,
            data_resposta=datetime.utcnow()
        )
        db_session.add(nova_resposta)

        # Atualizar status baseado na ação
        if acao == 'resolver':
            ticket.status = 'respondido'
            ticket.data_resolucao = datetime.utcnow()
        else:
            ticket.status = 'em_andamento'

        # Notificar o usuário
        notificacao_usuario = Notificacao(
            usuario_id=ticket.usuario_id,
            tipo='ticket',
            titulo='Resposta ao Seu Ticket',
            mensagem=f'Seu ticket "{ticket.assunto}" recebeu uma resposta da administração',
            link_acao=f'/tickets/{ticket.id}'
        )
        db_session.add(notificacao_usuario)

        db_session.commit()

        flash('Resposta enviada com sucesso!', 'success')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))

    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao enviar resposta: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))


@admin_tickets_bp.route('/<int:ticket_id>/fechar', methods=['POST'])
def fechar_ticket(ticket_id):
    """Fechar um ticket"""
    try:
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
            mensagem=f'Seu ticket "{ticket.assunto}" foi fechado pela administração',
            link_acao=f'/tickets/{ticket.id}'
        )
        db_session.add(notificacao)

        db_session.commit()

        flash('Ticket fechado com sucesso.', 'success')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))

    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao fechar ticket: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))


@admin_tickets_bp.route('/<int:ticket_id>/reabrir', methods=['POST'])
def reabrir_ticket(ticket_id):
    """Reabrir um ticket fechado"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            flash('Ticket não encontrado.', 'error')
            return redirect(url_for('admin_tickets.lista_tickets'))

        ticket.status = 'em_andamento'
        ticket.data_resolucao = None

        db_session.commit()

        flash('Ticket reaberto com sucesso.', 'success')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))

    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao reabrir ticket: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))


@admin_tickets_bp.route('/<int:ticket_id>/prioridade', methods=['POST'])
def alterar_prioridade(ticket_id):
    """Alterar prioridade do ticket (API)"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket não encontrado'}), 404

        data = request.get_json()
        nova_prioridade = data.get('prioridade')

        if nova_prioridade not in ['baixa', 'media', 'alta', 'urgente']:
            return jsonify({'success': False, 'error': 'Prioridade inválida'}), 400

        ticket.prioridade = nova_prioridade
        db_session.commit()

        return jsonify({'success': True, 'nova_prioridade': nova_prioridade})

    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_tickets_bp.route('/api/estatisticas')
def estatisticas_api():
    """API para estatísticas de tickets"""
    try:
        estatisticas = {
            'total_tickets': db_session.query(TicketSuporte).count(),
            'tickets_abertos': db_session.query(TicketSuporte).filter_by(status='aberto').count(),
            'tickets_em_andamento': db_session.query(TicketSuporte).filter_by(status='em_andamento').count(),
            'tickets_respondidos': db_session.query(TicketSuporte).filter_by(status='respondido').count(),
            'tickets_fechados': db_session.query(TicketSuporte).filter_by(status='fechado').count(),
            'tickets_urgentes': db_session.query(TicketSuporte).filter_by(prioridade='urgente',
                                                                          status='aberto').count(),
        }

        return jsonify({'success': True, 'estatisticas': estatisticas})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_tickets_bp.route('/api/recentes')
def tickets_recentes_api():
    """API para tickets recentes"""
    try:
        tickets = db_session.query(TicketSuporte).order_by(
            TicketSuporte.data_abertura.desc()
        ).limit(10).all()

        dados_tickets = []
        for ticket in tickets:
            dados_tickets.append({
                'id': ticket.id,
                'assunto': ticket.assunto,
                'usuario_nome': ticket.usuario.nome,
                'status': ticket.status,
                'prioridade': ticket.prioridade,
                'data_abertura': ticket.data_abertura.strftime('%d/%m/%Y %H:%M'),
                'dias_aberto': (datetime.utcnow() - ticket.data_abertura).days
            })

        return jsonify({'success': True, 'tickets': dados_tickets})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_tickets_bp.route('/<int:ticket_id>/delete', methods=['POST'])
def deletar_ticket(ticket_id):
    """Deletar um ticket (apenas para limpeza)"""
    try:
        ticket = db_session.query(TicketSuporte).get(ticket_id)

        if not ticket:
            flash('Ticket não encontrado.', 'error')
            return redirect(url_for('admin_tickets.lista_tickets'))

        # Deletar respostas primeiro
        db_session.query(TicketResposta).filter_by(ticket_id=ticket_id).delete()

        # Deletar ticket
        db_session.delete(ticket)
        db_session.commit()

        flash('Ticket deletado com sucesso.', 'success')
        return redirect(url_for('admin_tickets.lista_tickets'))

    except Exception as e:
        db_session.rollback()
        flash(f'Erro ao deletar ticket: {str(e)}', 'error')
        return redirect(url_for('admin_tickets.detalhes_ticket', ticket_id=ticket_id))