# blueprints/chat.py
from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db_session
from models import Conversa, Mensagem, Agendamento, Usuario, PrestadorServico, Notificacao, Servico
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')


@chat_bp.route('/')
@login_required
def index():
    """Página principal do chat - lista de conversas CORRIGIDA"""
    try:
        print(f"🔍 CARREGANDO CONVERSAS - Usuário: {current_user.id}, Tipo: {current_user.tipo}")

        # Buscar conversas do usuário
        if current_user.tipo == 'cliente':
            conversas = db_session.query(Conversa).filter_by(cliente_id=current_user.id).all()
            print(f"✅ Cliente: {len(conversas)} conversas encontradas")
        else:
            conversas = db_session.query(Conversa).filter_by(prestador_id=current_user.id).all()
            print(f"✅ Prestador: {len(conversas)} conversas encontradas")

        # Buscar informações completas para cada conversa
        conversas_completas = []
        for conversa in conversas:
            try:
                # Buscar agendamento
                agendamento = db_session.query(Agendamento).get(conversa.agendamento_id)
                if not agendamento:
                    continue

                # Buscar serviço
                servico = db_session.query(Servico).get(agendamento.servico_id)
                if not servico:
                    continue

                # Buscar informações do outro usuário
                if current_user.tipo == 'cliente':
                    # Para cliente, buscar prestador
                    prestador = db_session.query(PrestadorServico).get(agendamento.prestador_id)
                    if prestador:
                        outro_usuario = db_session.query(Usuario).get(prestador.usuario_id)
                        outro_nome = outro_usuario.nome if outro_usuario else "Prestador"
                        especialidade = prestador.especialidade
                    else:
                        outro_nome = "Prestador"
                        especialidade = ""
                else:
                    # Para prestador, buscar cliente
                    cliente = db_session.query(Usuario).get(agendamento.cliente_id)
                    outro_nome = cliente.nome if cliente else "Cliente"
                    especialidade = "Cliente"

                # Buscar última mensagem
                ultima_mensagem = db_session.query(Mensagem).filter_by(
                    conversa_id=conversa.id
                ).order_by(Mensagem.data_envio.desc()).first()

                # Contar mensagens não lidas
                mensagens_nao_lidas = db_session.query(Mensagem).filter_by(
                    conversa_id=conversa.id,
                    lida=False
                ).filter(Mensagem.remetente_id != current_user.id).count()

                conversas_completas.append({
                    'conversa': conversa,
                    'agendamento': agendamento,
                    'servico': servico,
                    'outro_nome': outro_nome,
                    'especialidade': especialidade,
                    'ultima_mensagem': ultima_mensagem,
                    'mensagens_nao_lidas': mensagens_nao_lidas
                })

                print(f"📋 Conversa {conversa.id}: {outro_nome} - {mensagens_nao_lidas} não lidas")

            except Exception as e:
                print(f"⚠️  Erro ao processar conversa {conversa.id}: {e}")
                continue

        print(f"🎯 Total de conversas processadas: {len(conversas_completas)}")
        return render_template('chat/index.html', conversas=conversas_completas)

    except Exception as e:
        print(f"🔥 ERRO ao carregar conversas: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar conversas', 'error')
        return render_template('chat/index.html', conversas=[])


# 🔧 ROTA DE DEBUG - ADICIONE ISSO NO FINAL DO ARQUIVO
@chat_bp.route('/debug-conversas')
@login_required
def debug_conversas():
    """Rota de debug para verificar conversas"""
    try:
        print(f"=== 🚨 DEBUG CONVERSAS ===")
        print(f"Usuário: {current_user.id}, Tipo: {current_user.tipo}")

        if current_user.tipo == 'cliente':
            conversas = db_session.query(Conversa).filter_by(cliente_id=current_user.id).all()
        else:
            conversas = db_session.query(Conversa).filter_by(prestador_id=current_user.id).all()

        print(f"Total de conversas no banco: {len(conversas)}")

        for i, conversa in enumerate(conversas):
            print(f"Conversa {i + 1}:")
            print(f"  ID: {conversa.id}")
            print(f"  Agendamento ID: {conversa.agendamento_id}")
            print(f"  Cliente ID: {conversa.cliente_id}")
            print(f"  Prestador ID: {conversa.prestador_id}")

            # Buscar agendamento
            agendamento = db_session.query(Agendamento).get(conversa.agendamento_id)
            if agendamento:
                print(f"  Agendamento Status: {agendamento.status}")
                print(f"  Serviço ID: {agendamento.servico_id}")
            else:
                print("  ❌ Agendamento não encontrado!")

        print("=== ✅ FIM DEBUG ===")

        return f"""
        <h1>Debug Conversas</h1>
        <p>Usuário: {current_user.id} ({current_user.tipo})</p>
        <p>Total conversas: {len(conversas)}</p>
        <pre>{[c.id for c in conversas]}</pre>
        <a href="/chat">Voltar</a>
        """

    except Exception as e:
        return f"Erro: {str(e)}", 500

# blueprints/chat.py - ADICIONE ESTA ROTA
@chat_bp.route('/api/websocket-token')
@login_required
def websocket_token():
    """Gerar token para WebSocket (se implementar)"""
    return jsonify({
        'success': True,
        'user_id': current_user.id,
        'token': 'ws-token-placeholder'  # Implementar geração real de token
    })


# blueprints/chat.py - ROTA CONVERSA ULTRA SEGURA

@chat_bp.route('/conversa-segura/<int:agendamento_id>')
@login_required
def conversa_segura(agendamento_id):
    """Página de conversa - VERSÃO ULTRA SEGURA SEM .usuario"""
    try:
        print(f"🛡️  CONVERSA SEGURA - Iniciando...")

        # 1. Buscar apenas dados essenciais
        agendamento = db_session.query(Agendamento).get(agendamento_id)
        if not agendamento:
            flash('Agendamento não encontrado.', 'error')
            return redirect(url_for('chat.index'))

        # 2. Verificação MUITO simples
        if current_user.tipo == 'cliente' and agendamento.cliente_id != current_user.id:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('chat.index'))

        # 3. Buscar conversa existente ou criar nova SEM .usuario
        conversa = db_session.query(Conversa).filter_by(agendamento_id=agendamento_id).first()

        if not conversa:
            print("Criando nova conversa...")
            # Buscar prestador de forma DIRETA
            prestador = db_session.query(PrestadorServico).get(agendamento.prestador_id)
            if not prestador:
                flash('Prestador não encontrado.', 'error')
                return redirect(url_for('chat.index'))

            # Criar conversa SEM .usuario
            conversa = Conversa(
                agendamento_id=agendamento_id,
                cliente_id=agendamento.cliente_id,
                prestador_id=prestador.usuario_id,  # ✅ CORRETO: usuario_id direto
                data_criacao=datetime.utcnow(),
                ultima_mensagem=datetime.utcnow()
            )
            db_session.add(conversa)
            db_session.commit()

        # 4. Buscar mensagens
        mensagens = db_session.query(Mensagem).filter_by(conversa_id=conversa.id).order_by(Mensagem.data_envio).all()

        # 5. Marcar mensagens como lidas
        for msg in mensagens:
            if msg.remetente_id != current_user.id and not msg.lida:
                msg.lida = True
        db_session.commit()

        # 6. Buscar nomes para display de forma SEGURA
        cliente_nome = db_session.query(Usuario).get(agendamento.cliente_id).nome
        prestador_nome = db_session.query(Usuario).get(
            db_session.query(PrestadorServico).get(agendamento.prestador_id).usuario_id
        ).nome

        print(f"✅ Dados preparados: Cliente={cliente_nome}, Prestador={prestador_nome}")

        return render_template('chat/conversa_segura.html',
                               conversa=conversa,
                               mensagens=mensagens,
                               agendamento=agendamento,
                               cliente_nome=cliente_nome,
                               prestador_nome=prestador_nome)

    except Exception as e:
        print(f"🔥 ERRO NA CONVERSA SEGURA: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Erro ao carregar a conversa.', 'error')
        return redirect(url_for('chat.index'))

# blueprints/chat.py - CORRIJA TAMBÉM A ROTA conversa

# blueprints/chat.py - CORREÇÃO ESPECÍFICA PARA CLIENTE

# blueprints/chat.py - ROTA CONVERSA FUNCIONAL IMEDIATA

@chat_bp.route('/conversa/<int:agendamento_id>')
@login_required
def conversa(agendamento_id):
    """Página de conversa - VERSÃO QUE FUNCIONA AGORA"""
    try:
        print(f"🎯 INICIANDO CONVERSA - Agendamento: {agendamento_id}")

        # 1. Buscar agendamento básico
        agendamento = db_session.query(Agendamento).get(agendamento_id)
        if not agendamento:
            flash('Agendamento não encontrado.', 'error')
            return redirect(url_for('main.dashboard'))

        # 2. Verificação simples de permissão
        if current_user.tipo == 'cliente':
            if agendamento.cliente_id != current_user.id:
                flash('Acesso não autorizado.', 'error')
                return redirect(url_for('main.dashboard'))
        else:
            # Para prestador, verificar de forma segura
            prestador_atual = db_session.query(PrestadorServico).filter_by(usuario_id=current_user.id).first()
            if not prestador_atual or agendamento.prestador_id != prestador_atual.id:
                flash('Acesso não autorizado.', 'error')
                return redirect(url_for('main.dashboard'))

        # 3. Buscar ou criar conversa de forma SEGURA
        conversa = db_session.query(Conversa).filter_by(agendamento_id=agendamento_id).first()

        if not conversa:
            print("Criando nova conversa...")
            # Buscar prestador
            prestador = db_session.query(PrestadorServico).get(agendamento.prestador_id)
            if not prestador:
                flash('Prestador não encontrado.', 'error')
                return redirect(url_for('main.dashboard'))

            # Criar conversa
            conversa = Conversa(
                agendamento_id=agendamento_id,
                cliente_id=agendamento.cliente_id,
                prestador_id=prestador.usuario_id,  # ✅ CORRETO
                data_criacao=datetime.utcnow(),
                ultima_mensagem=datetime.utcnow()
            )
            db_session.add(conversa)
            db_session.commit()
            print(f"Conversa criada: {conversa.id}")

        # 4. Buscar mensagens
        mensagens = db_session.query(Mensagem).filter_by(conversa_id=conversa.id).order_by(Mensagem.data_envio).all()

        # 5. Marcar mensagens como lidas
        for msg in mensagens:
            if msg.remetente_id != current_user.id and not msg.lida:
                msg.lida = True
        db_session.commit()

        # 6. Buscar nomes para display de forma SEGURA
        cliente = db_session.query(Usuario).get(agendamento.cliente_id)
        prestador_obj = db_session.query(PrestadorServico).get(agendamento.prestador_id)
        prestador_usuario = db_session.query(Usuario).get(prestador_obj.usuario_id) if prestador_obj else None

        # 7. Renderizar template EXISTENTE com dados seguros
        return render_template('chat/conversa.html',
                               conversa=conversa,
                               mensagens=mensagens,
                               agendamento=agendamento,
                               cliente=cliente,
                               prestador_usuario=prestador_usuario)

    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Erro ao carregar conversa: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@chat_bp.route('/api/enviar', methods=['POST'])
@login_required
def enviar_mensagem():
    """API: Enviar mensagem"""
    try:
        data = request.get_json()

        if not data or 'conversa_id' not in data or 'mensagem' not in data:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400

        conversa_id = data['conversa_id']
        conteudo = data['mensagem'].strip()

        if not conteudo:
            return jsonify({'success': False, 'error': 'Mensagem vazia'}), 400

        # Verificar se a conversa existe e o usuário tem acesso
        conversa = db_session.query(Conversa).get(conversa_id)
        if not conversa:
            return jsonify({'success': False, 'error': 'Conversa não encontrada'}), 404

        # Verificar se o usuário tem acesso à conversa
        if current_user.id not in [conversa.cliente_id, conversa.prestador_id]:
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        # Criar mensagem
        nova_mensagem = Mensagem(
            conversa_id=conversa_id,
            remetente_id=current_user.id,
            conteudo=conteudo,
            tipo='texto',
            data_envio=datetime.utcnow(),
            lida=False
        )

        # Atualizar última mensagem da conversa
        conversa.ultima_mensagem = datetime.utcnow()

        db_session.add(nova_mensagem)
        db_session.commit()

        # Criar notificação para o outro usuário
        outro_usuario_id = conversa.cliente_id if current_user.id == conversa.prestador_id else conversa.prestador_id

        notificacao = Notificacao(
            usuario_id=outro_usuario_id,
            tipo='mensagem',
            titulo='Nova Mensagem',
            mensagem=f'{current_user.nome}: {conteudo[:50]}{"..." if len(conteudo) > 50 else ""}',
            link_acao=f'/chat/conversa/{conversa.agendamento_id}',
            data_criacao=datetime.utcnow()
        )
        db_session.add(notificacao)
        db_session.commit()

        return jsonify({
            'success': True,
            'mensagem_id': nova_mensagem.id,
            'data_envio': nova_mensagem.data_envio.isoformat()
        })

    except Exception as e:
        db_session.rollback()
        print(f"🔥 ERRO ao enviar mensagem: {str(e)}")
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


# blueprints/chat.py - ADICIONE ESTA ROTA DE DEBUG

@chat_bp.route('/debug-conversa/<int:agendamento_id>')
@login_required
def debug_conversa(agendamento_id):
    """Rota de debug para encontrar o erro exato"""
    try:
        print("=== 🚨 INÍCIO DO DEBUG ===")
        print(f"Usuário: {current_user.id}, Tipo: {current_user.tipo}")

        # Teste 1: Buscar agendamento
        agendamento = db_session.query(Agendamento).get(agendamento_id)
        print(f"1. Agendamento: {agendamento.id if agendamento else 'None'}")

        # Teste 2: Verificar permissões
        if current_user.tipo == 'cliente':
            print(f"2. Cliente ID: {current_user.id}, Agendamento Cliente ID: {agendamento.cliente_id}")

        # Teste 3: Buscar conversa
        conversa = db_session.query(Conversa).filter_by(agendamento_id=agendamento_id).first()
        print(f"3. Conversa: {conversa.id if conversa else 'None'}")

        # Teste 4: Buscar prestador
        prestador = db_session.query(PrestadorServico).get(agendamento.prestador_id)
        print(f"4. Prestador: {prestador.id if prestador else 'None'}")

        # Teste 5: Buscar usuário do prestador
        if prestador:
            prestador_usuario = db_session.query(Usuario).get(prestador.usuario_id)
            print(f"5. Prestador Usuário: {prestador_usuario.nome if prestador_usuario else 'None'}")

        # Teste 6: Buscar cliente
        cliente = db_session.query(Usuario).get(agendamento.cliente_id)
        print(f"6. Cliente: {cliente.nome if cliente else 'None'}")

        print("=== ✅ FIM DO DEBUG - TODOS OS TESTES PASSARAM ===")

        # Se chegou aqui, renderizar template básico
        return render_template('chat/debug.html',
                               agendamento=agendamento,
                               conversa=conversa)

    except Exception as e:
        print(f"=== ❌ ERRO NO DEBUG: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return f"ERRO: {str(e)}", 500



@chat_bp.route('/iniciar/<int:agendamento_id>', methods=['POST'])
@login_required
def iniciar_conversa(agendamento_id):
    """Iniciar conversa - CORRIGIDA PARA CLIENTE"""
    try:
        print(
            f"🔍 INICIANDO CONVERSA - Agendamento: {agendamento_id}, Usuário: {current_user.id}, Tipo: {current_user.tipo}")

        # 1. Buscar agendamento
        agendamento = db_session.query(Agendamento).get(agendamento_id)
        if not agendamento:
            print("❌ Agendamento não encontrado")
            return jsonify({'success': False, 'error': 'Agendamento não encontrado'}), 404

        print(f"📋 Agendamento encontrado: ID {agendamento.id}")

        # 2. Verificar permissões - CORREÇÃO PARA CLIENTE
        if current_user.tipo == 'cliente':
            if agendamento.cliente_id != current_user.id:
                print(f"❌ Cliente {current_user.id} não é o cliente do agendamento {agendamento.cliente_id}")
                return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403
            print("✅ Cliente autorizado")
        else:  # prestador
            # Para prestador, verificar de forma segura sem acessar current_user.prestador diretamente
            prestador_atual = db_session.query(PrestadorServico).filter_by(usuario_id=current_user.id).first()
            if not prestador_atual or agendamento.prestador_id != prestador_atual.id:
                print(f"❌ Prestador {current_user.id} não é o prestador do agendamento {agendamento.prestador_id}")
                return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403
            print("✅ Prestador autorizado")

        # 3. Verificar se conversa já existe
        conversa_existente = db_session.query(Conversa).filter_by(
            agendamento_id=agendamento_id
        ).first()

        if conversa_existente:
            print(f"✅ Conversa já existe: ID {conversa_existente.id}")
            return jsonify({
                'success': True,
                'conversa_id': conversa_existente.id,
                'message': 'Conversa já existe',
                'redirect': True
            })

        # 4. Criar nova conversa
        print("🆕 Criando nova conversa...")

        # Buscar o prestador para obter seu usuario_id
        prestador = db_session.query(PrestadorServico).get(agendamento.prestador_id)
        if not prestador:
            return jsonify({'success': False, 'error': 'Prestador não encontrado'}), 404

        nova_conversa = Conversa(
            agendamento_id=agendamento_id,
            cliente_id=agendamento.cliente_id,
            prestador_id=prestador.usuario_id,  # ✅ Usar usuario_id do prestador
            data_criacao=datetime.utcnow(),
            ultima_mensagem=datetime.utcnow()
        )

        db_session.add(nova_conversa)
        db_session.flush()
        print(f"✅ Nova conversa criada: ID {nova_conversa.id}")

        # 5. Criar mensagem de boas-vindas automática
        mensagem_boas_vindas = Mensagem(
            conversa_id=nova_conversa.id,
            remetente_id=current_user.id,
            conteudo="Olá! Iniciamos nossa conversa sobre o serviço agendado.",
            tipo='texto',
            data_envio=datetime.utcnow(),
            lida=False
        )

        db_session.add(mensagem_boas_vindas)
        db_session.commit()
        print("💾 Conversa salva no banco")

        # 6. Criar notificação para o outro usuário
        if current_user.tipo == 'cliente':
            # Cliente iniciando conversa -> notificar prestador
            outro_usuario_id = prestador.usuario_id
        else:
            # Prestador iniciando conversa -> notificar cliente
            outro_usuario_id = agendamento.cliente_id

        notificacao = Notificacao(
            usuario_id=outro_usuario_id,
            tipo='mensagem',
            titulo='Nova Conversa Iniciada',
            mensagem=f'{current_user.nome} iniciou uma conversa sobre o serviço "{agendamento.servico.titulo}"',
            link_acao=f'/chat/conversa/{agendamento_id}',
            data_criacao=datetime.utcnow()
        )
        db_session.add(notificacao)
        db_session.commit()

        print(f"🔔 Notificação criada para usuário {outro_usuario_id}")

        return jsonify({
            'success': True,
            'conversa_id': nova_conversa.id,
            'message': 'Conversa iniciada com sucesso!',
            'redirect': True
        })

    except Exception as e:
        db_session.rollback()
        print(f"🔥 ERRO CRÍTICO ao iniciar conversa: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500



@chat_bp.route('/api/mensagens/<int:conversa_id>', methods=['GET'])
@login_required
def obter_mensagens(conversa_id):
    """API: Obter mensagens de uma conversa"""
    try:
        # Verificar permissão
        conversa = db_session.query(Conversa).get(conversa_id)
        if not conversa or (current_user.id not in [conversa.cliente_id, conversa.prestador_id]):
            return jsonify({'error': 'Acesso não autorizado'}), 403

        mensagens = db_session.query(Mensagem).filter_by(conversa_id=conversa_id).order_by(Mensagem.data_envio).all()

        dados_mensagens = []
        for msg in mensagens:
            dados_mensagens.append({
                'id': msg.id,
                'remetente_id': msg.remetente_id,
                'conteudo': msg.conteudo,
                'tipo': msg.tipo,
                'data_envio': msg.data_envio.isoformat(),
                'lida': msg.lida
            })

        return jsonify({
            'success': True,
            'mensagens': dados_mensagens,
            'conversa_id': conversa_id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




@chat_bp.route('/api/conversas', methods=['GET'])
@login_required
def listar_conversas():
    """API: Listar conversas do usuário"""
    try:
        if current_user.tipo == 'cliente':
            conversas = db_session.query(Conversa).filter_by(cliente_id=current_user.id).all()
        else:
            conversas = db_session.query(Conversa).filter_by(prestador_id=current_user.id).all()

        dados_conversas = []
        for conv in conversas:
            # Obter última mensagem
            ultima_msg = db_session.query(Mensagem).filter_by(conversa_id=conv.id).order_by(
                Mensagem.data_envio.desc()).first()

            # Contar mensagens não lidas
            mensagens_nao_lidas = db_session.query(Mensagem).filter_by(
                conversa_id=conv.id,
                lida=False
            ).filter(Mensagem.remetente_id != current_user.id).count()

            # Determinar o outro usuário
            if current_user.tipo == 'cliente':
                outro_usuario = conv.prestador.usuario
                categoria = conv.prestador.categoria
            else:
                outro_usuario = conv.cliente
                categoria = 'Cliente'

            dados_conversas.append({
                'id': conv.id,
                'agendamento_id': conv.agendamento_id,
                'outro_usuario': {
                    'id': outro_usuario.id,
                    'nome': outro_usuario.nome,
                    'categoria': categoria
                },
                'ultima_mensagem': {
                    'conteudo': ultima_msg.conteudo if ultima_msg else 'Nenhuma mensagem',
                    'data': ultima_msg.data_envio.isoformat() if ultima_msg else conv.data_criacao.isoformat()
                } if ultima_msg else None,
                'mensagens_nao_lidas': mensagens_nao_lidas,
                'servico_titulo': conv.agendamento.servico.titulo
            })

        return jsonify({
            'success': True,
            'conversas': dados_conversas
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500






@chat_bp.route('/api/marcar-lidas/<int:conversa_id>', methods=['POST'])
@login_required
def marcar_mensagens_lidas(conversa_id):
    """API: Marcar mensagens como lidas"""
    try:
        conversa = db_session.query(Conversa).get(conversa_id)
        if not conversa or (current_user.id not in [conversa.cliente_id, conversa.prestador_id]):
            return jsonify({'success': False, 'error': 'Acesso não autorizado'}), 403

        # Marcar todas as mensagens não lidas como lidas
        mensagens_nao_lidas = db_session.query(Mensagem).filter_by(
            conversa_id=conversa_id,
            lida=False
        ).filter(Mensagem.remetente_id != current_user.id).all()

        for msg in mensagens_nao_lidas:
            msg.lida = True

        db_session.commit()

        return jsonify({'success': True, 'marcadas': len(mensagens_nao_lidas)})

    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



