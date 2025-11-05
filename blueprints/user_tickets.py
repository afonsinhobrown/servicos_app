from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import TicketSuporte, TicketResposta, Notificacao, Usuario
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


@tickets_bp.route('/')
@login_required
def meus_tickets():
    """Lista os tickets do usuário atual"""
    tickets = db_session.query(TicketSuporte).filter_by(
        usuario_id=current_user.id
    ).order_by(TicketSuporte.data_abertura.desc()).all()

    return render_template('tickets/meus_tickets.html', tickets=tickets)


@tickets_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_ticket():
    """Criar novo ticket"""
    if request.method == 'POST':
        assunto = request.form.get('assunto')
        descricao = request.form.get('descricao')
        categoria = request.form.get('categoria')

        if not assunto or not descricao:
            flash('Assunto e descrição são obrigatórios.', 'warning')
            return render_template('tickets/novo_ticket.html')

        novo_ticket = TicketSuporte(
            usuario_id=current_user.id,
            assunto=assunto,
            descricao=descricao,
            categoria=categoria,
            status='aberto',
            data_abertura=datetime.utcnow()
        )

        db_session.add(novo_ticket)
        db_session.commit()

        flash('Ticket criado com sucesso!', 'success')
        return redirect(url_for('tickets.meus_tickets'))

    return render_template('tickets/novo_ticket.html')


@tickets_bp.route('/<int:ticket_id>')
@login_required
def detalhes_ticket(ticket_id):
    """Detalhes de um ticket específico do usuário"""
    try:
        print(f"🚀 DEBUG: Usuário {current_user.id} acessando ticket {ticket_id}")

        # Verificar se o ticket pertence ao usuário
        ticket = db_session.query(TicketSuporte).filter_by(
            id=ticket_id,
            usuario_id=current_user.id
        ).first()

        if not ticket:
            print("❌ DEBUG: Ticket não encontrado ou sem acesso")
            flash('Ticket não encontrado ou você não tem acesso.', 'error')
            return redirect(url_for('tickets.meus_tickets'))

        print(f"✅ DEBUG: Ticket encontrado - ID: {ticket.id}, Assunto: {ticket.assunto}")

        # Buscar respostas (versão simples)
        respostas = db_session.query(TicketResposta).filter_by(
            ticket_id=ticket_id
        ).order_by(TicketResposta.data_resposta.asc()).all()

        print(f"📝 DEBUG: Encontradas {len(respostas)} respostas")

        # Carregar informações dos usuários manualmente
        for i, resposta in enumerate(respostas):
            usuario_resposta = db_session.query(Usuario).get(resposta.usuario_id)
            print(
                f"📄 DEBUG - Resposta {i + 1}: ID={resposta.id}, Usuário={resposta.usuario_id}, Tipo={usuario_resposta.tipo}, Nome={usuario_resposta.nome}")

        return render_template('tickets/detalhes_ticket.html',
                               ticket=ticket,
                               respostas=respostas)

    except Exception as e:
        print(f"💥 ERRO em detalhes_ticket: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        flash(f'Erro ao carregar ticket: {str(e)}', 'error')
        return redirect(url_for('tickets.meus_tickets'))


@tickets_bp.route('/<int:ticket_id>/responder', methods=['POST'])
@login_required
def responder_ticket(ticket_id):
    """Usuário responde a um ticket"""
    ticket = db_session.query(TicketSuporte).filter_by(
        id=ticket_id,
        usuario_id=current_user.id
    ).first()

    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('tickets.meus_tickets'))

    resposta = request.form.get('resposta')

    if not resposta:
        flash('Por favor, escreva uma resposta.', 'warning')
        return redirect(url_for('tickets.detalhes_ticket', ticket_id=ticket_id))

    nova_resposta = TicketResposta(
        ticket_id=ticket_id,
        usuario_id=current_user.id,
        resposta=resposta,
        data_resposta=datetime.utcnow()
    )

    # Atualizar status do ticket
    ticket.status = 'em_andamento'

    db_session.add(nova_resposta)
    db_session.commit()

    flash('Resposta enviada com sucesso!', 'success')
    return redirect(url_for('tickets.detalhes_ticket', ticket_id=ticket_id))


@tickets_bp.route('/<int:ticket_id>/fechar', methods=['POST'])
@login_required
def fechar_ticket(ticket_id):
    """Usuário fecha um ticket"""
    ticket = db_session.query(TicketSuporte).filter_by(
        id=ticket_id,
        usuario_id=current_user.id
    ).first()

    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('tickets.meus_tickets'))

    ticket.status = 'fechado'
    ticket.data_resolucao = datetime.utcnow()

    db_session.commit()

    flash('Ticket fechado com sucesso.', 'success')
    return redirect(url_for('tickets.meus_tickets'))


@tickets_bp.route('/<int:ticket_id>/reabrir', methods=['POST'])
@login_required
def reabrir_ticket(ticket_id):
    """Usuário reabre um ticket fechado"""
    ticket = db_session.query(TicketSuporte).filter_by(
        id=ticket_id,
        usuario_id=current_user.id
    ).first()

    if not ticket:
        flash('Ticket não encontrado.', 'error')
        return redirect(url_for('tickets.meus_tickets'))

    ticket.status = 'aberto'
    ticket.data_resolucao = None

    db_session.commit()

    flash('Ticket reaberto com sucesso.', 'success')
    return redirect(url_for('tickets.detalhes_ticket', ticket_id=ticket_id))


@tickets_bp.route('/api/estatisticas')
@login_required
def estatisticas_tickets():
    """API: Estatísticas dos tickets do usuário"""
    try:
        total_tickets = db_session.query(TicketSuporte).filter_by(
            usuario_id=current_user.id
        ).count()

        tickets_abertos = db_session.query(TicketSuporte).filter_by(
            usuario_id=current_user.id,
            status='aberto'
        ).count()

        tickets_em_andamento = db_session.query(TicketSuporte).filter_by(
            usuario_id=current_user.id,
            status='em_andamento'
        ).count()

        tickets_fechados = db_session.query(TicketSuporte).filter_by(
            usuario_id=current_user.id,
            status='fechado'
        ).count()

        return jsonify({
            'success': True,
            'estatisticas': {
                'total_tickets': total_tickets,
                'tickets_abertos': tickets_abertos,
                'tickets_em_andamento': tickets_em_andamento,
                'tickets_fechados': tickets_fechados
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tickets_bp.route('/api/recentes')
@login_required
def tickets_recentes():
    """API: Tickets recentes do usuário"""
    try:
        tickets = db_session.query(TicketSuporte).filter_by(
            usuario_id=current_user.id
        ).order_by(TicketSuporte.data_abertura.desc()).limit(5).all()

        dados_tickets = []
        for ticket in tickets:
            dados_tickets.append({
                'id': ticket.id,
                'assunto': ticket.assunto,
                'status': ticket.status,
                'prioridade': ticket.prioridade,
                'data_abertura': ticket.data_abertura.strftime('%d/%m/%Y %H:%M'),
                'dias_aberto': (datetime.utcnow() - ticket.data_abertura).days
            })

        return jsonify({'success': True, 'tickets': dados_tickets})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500