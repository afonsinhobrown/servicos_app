BEGIN TRANSACTION;;
CREATE TABLE `agendamentos` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `cliente_id` INTEGER NOT NULL,
  `prestador_id` INTEGER NOT NULL,
  `servico_id` INTEGER NOT NULL,
  `data_agendamento` TEXT NOT NULL,
  `status` TEXT,
  `observacoes` TEXT,
  `endereco_servico` TEXT,
  `modalidade` TEXT,
  `criado_em` TEXT,
  `atualizado_em` TEXT,
  FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`prestador_id`) REFERENCES `prestadores_servico` (`id`),
  FOREIGN KEY (`servico_id`) REFERENCES `servicos` (`id`)
);;
INSERT INTO "agendamentos" VALUES(1,13,1,1,'2025-11-08 15:00:00','realizado','','hhjhhjj mn','presencial','2025-10-30 23:16:03','2025-11-04 16:30:53');;
CREATE TABLE `avaliacoes` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `agendamento_id` INTEGER,
  `cliente_id` INTEGER,
  `prestador_id` INTEGER,
  `rating` INTEGER,
  `comentario` TEXT,
  `anonima` INTEGER,
  `data_avaliacao` TEXT,
  `resposta_prestador` TEXT,
  `data_resposta` TEXT,
  FOREIGN KEY (`agendamento_id`) REFERENCES `agendamentos` (`id`),
  FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`prestador_id`) REFERENCES `prestadores_servico` (`id`)
);;
INSERT INTO "avaliacoes" VALUES(1,1,13,1,1,'',0,'2025-11-04 14:55:18','Não é justo. Peço para rever','2025-11-04 15:39:42');;
CREATE TABLE `categorias_servico` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nome` TEXT NOT NULL,
  `slug` TEXT NOT NULL,
  `descricao` TEXT,
  `icone` TEXT,
  `ativa` INTEGER,
  `ordem` INTEGER,
  UNIQUE (`slug`)
);;
INSERT INTO "categorias_servico" VALUES(1,'Médico','medico',NULL,'heart-pulse',1,1);;
INSERT INTO "categorias_servico" VALUES(2,'Psicólogo','psicologo',NULL,'brain',1,2);;
INSERT INTO "categorias_servico" VALUES(3,'Personal Trainer','personal_trainer',NULL,'activity',1,3);;
INSERT INTO "categorias_servico" VALUES(4,'Cozinheiro','cozinheiro',NULL,'egg-fried',1,4);;
INSERT INTO "categorias_servico" VALUES(5,'Advogado','advogado',NULL,'briefcase',1,5);;
INSERT INTO "categorias_servico" VALUES(6,'Consultor','consultor',NULL,'graph-up',1,6);;
CREATE TABLE `configuracoes_plataforma` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `chave` TEXT NOT NULL,
  `valor` TEXT,
  `tipo` TEXT,
  `descricao` TEXT,
  `atualizado_em` TEXT,
  UNIQUE (`chave`)
);;
CREATE TABLE `conversas` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `agendamento_id` INTEGER NOT NULL,
  `cliente_id` INTEGER NOT NULL,
  `prestador_id` INTEGER NOT NULL,
  `data_criacao` TEXT,
  `ultima_mensagem` TEXT,
  FOREIGN KEY (`agendamento_id`) REFERENCES `agendamentos` (`id`),
  FOREIGN KEY (`cliente_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`prestador_id`) REFERENCES `usuarios` (`id`)
);;
INSERT INTO "conversas" VALUES(1,1,13,1,'2025-10-31 10:55:29','2025-11-04 23:50:00');;
CREATE TABLE `documentos_prestador` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `prestador_id` INTEGER,
  `tipo_documento` TEXT,
  `nome_arquivo` TEXT,
  `arquivo_url` TEXT,
  `status_verificacao` TEXT,
  `observacoes` TEXT,
  `data_upload` TEXT,
  `data_verificacao` TEXT,
  FOREIGN KEY (`prestador_id`) REFERENCES `prestadores_servico` (`id`)
);;
CREATE TABLE `mensagens` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `conversa_id` INTEGER NOT NULL,
  `remetente_id` INTEGER NOT NULL,
  `conteudo` TEXT NOT NULL,
  `tipo` TEXT,
  `arquivo_url` TEXT,
  `data_envio` TEXT,
  `lida` INTEGER,
  FOREIGN KEY (`conversa_id`) REFERENCES `conversas` (`id`),
  FOREIGN KEY (`remetente_id`) REFERENCES `usuarios` (`id`)
);;
INSERT INTO "mensagens" VALUES(1,1,13,'Olá! Iniciamos nossa conversa sobre o serviço agendado.','texto',NULL,'2025-10-31 10:55:29',1);;
INSERT INTO "mensagens" VALUES(2,1,1,'Bom dia..mais uma vez','texto',NULL,'2025-10-31 12:39:33',1);;
INSERT INTO "mensagens" VALUES(3,1,13,'Estou disponivel para proximo sabado..','texto',NULL,'2025-10-31 12:41:14',1);;
INSERT INTO "mensagens" VALUES(4,1,13,'alo','texto',NULL,'2025-11-04 12:20:53',1);;
INSERT INTO "mensagens" VALUES(5,1,1,'bom dia Banze','texto',NULL,'2025-11-04 12:21:01',0);;
INSERT INTO "mensagens" VALUES(6,1,13,'estou bem','texto',NULL,'2025-11-04 12:21:14',1);;
INSERT INTO "mensagens" VALUES(7,1,1,'ok!isto funciona!','texto',NULL,'2025-11-04 12:21:31',0);;
INSERT INTO "mensagens" VALUES(8,1,13,'sim bro','texto',NULL,'2025-11-04 12:21:43',1);;
INSERT INTO "mensagens" VALUES(9,1,1,'altraçao na data','texto',NULL,'2025-11-04 13:36:10',0);;
INSERT INTO "mensagens" VALUES(10,1,1,'ok!isto funciona!','texto',NULL,'2025-11-04 23:50:00',0);;
CREATE TABLE `notificacoes` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `usuario_id` INTEGER,
  `tipo` TEXT,
  `titulo` TEXT,
  `mensagem` TEXT,
  `lida` INTEGER,
  `data_criacao` TEXT,
  `link_acao` TEXT,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
);;
INSERT INTO "notificacoes" VALUES(1,1,'agendamento','Novo Agendamento','Zayn Malik agendou seu serviço "Serviço de Culinária Internacional - Básico" para 08/11/2025 às 15:00',0,'2025-10-30 23:16:03','/agendamentos/1');;
INSERT INTO "notificacoes" VALUES(2,13,'mensagem','Nova Mensagem','João Maputo: Bom dia..mais uma vez',1,'2025-10-31 12:39:33','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(3,1,'mensagem','Nova Mensagem','Zayn Malik: Estou disponivel para proximo sabado..',0,'2025-10-31 12:41:14','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(4,1,'mensagem','Nova Mensagem','Zayn Malik: alo',0,'2025-11-04 12:20:53','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(5,13,'mensagem','Nova Mensagem','João Maputo: bom dia Banze',1,'2025-11-04 12:21:02','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(6,1,'mensagem','Nova Mensagem','Zayn Malik: estou bem',0,'2025-11-04 12:21:14','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(7,13,'mensagem','Nova Mensagem','João Maputo: ok!isto funciona!',1,'2025-11-04 12:21:31','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(8,1,'mensagem','Nova Mensagem','Zayn Malik: sim bro',0,'2025-11-04 12:21:43','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(9,13,'agendamento','Agendamento Confirmado','João Maputo confirmou seu agendamento para 08/11/2025 às 15:00',1,'2025-11-04 12:58:29','/agendamentos/1');;
INSERT INTO "notificacoes" VALUES(10,13,'mensagem','Nova Mensagem','João Maputo: altraçao na data',1,'2025-11-04 13:36:10','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(11,13,'agendamento','Serviço Concluído','O serviço "Serviço de Culinária Internacional - Básico" foi concluído por João Maputo. Por favor, avalie a experiência.',1,'2025-11-04 16:30:53','/agendamentos/1/avaliar');;
INSERT INTO "notificacoes" VALUES(12,1,'avaliacao','Nova Avaliação Recebida','Você recebeu uma avaliação de Zayn Malik',0,'2025-11-04 14:55:18','/avaliacoes/minhas');;
INSERT INTO "notificacoes" VALUES(13,13,'avaliacao','Resposta à Sua Avaliação','João Maputo respondeu sua avaliação',1,'2025-11-04 15:39:42','/avaliacoes/minhas');;
INSERT INTO "notificacoes" VALUES(14,15,'ticket','Novo Ticket de Suporte','Zayn Malik abriu um novo ticket: Nao meu chat nao funciona',0,'2025-11-04 23:39:13','/admin/tickets/None');;
INSERT INTO "notificacoes" VALUES(15,15,'ticket','Novo Ticket de Suporte','João Maputo abriu um novo ticket: Pagamentos',0,'2025-11-04 23:40:49','/admin/tickets/None');;
INSERT INTO "notificacoes" VALUES(16,1,'ticket','Resposta ao Seu Ticket','Seu ticket "Pagamentos" recebeu uma resposta da equipe',0,'2025-11-04 23:43:28','/tickets/2');;
INSERT INTO "notificacoes" VALUES(17,1,'ticket','Ticket Fechado','Seu ticket "Pagamentos" foi fechado pela equipe',0,'2025-11-04 23:43:35','/tickets/2');;
INSERT INTO "notificacoes" VALUES(18,15,'ticket','Novo Ticket de Suporte','João Maputo abriu um novo ticket: Pagamentos',0,'2025-11-04 23:45:31','/admin/tickets/None');;
INSERT INTO "notificacoes" VALUES(19,1,'ticket','Resposta ao Seu Ticket','Seu ticket "Pagamentos" recebeu uma resposta da equipe',0,'2025-11-04 23:46:56','/tickets/3');;
INSERT INTO "notificacoes" VALUES(20,13,'mensagem','Nova Mensagem','João Maputo: ok!isto funciona!',0,'2025-11-04 23:50:00','/chat/conversa/1');;
INSERT INTO "notificacoes" VALUES(21,1,'ticket','Resposta ao Seu Ticket','Seu ticket "Pagamentos" recebeu uma resposta da equipe',0,'2025-11-05 06:06:28','/tickets/3');;
INSERT INTO "notificacoes" VALUES(22,1,'ticket','Resposta ao Seu Ticket','Seu ticket "Pagamentos" recebeu uma resposta da administração',0,'2025-11-05 06:36:11','/tickets/3');;
INSERT INTO "notificacoes" VALUES(23,1,'ticket','Resposta ao Seu Ticket','Seu ticket "Pagamentos" recebeu uma resposta da administração',0,'2025-11-05 06:50:13','/tickets/3');;
CREATE TABLE `pagamentos` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `agendamento_id` INTEGER NOT NULL,
  `valor_total` REAL NOT NULL,
  `taxa_plataforma` REAL,
  `valor_prestador` REAL NOT NULL,
  `status` TEXT,
  `metodo_pagamento` TEXT,
  `id_transacao` TEXT,
  `data_pagamento` TEXT,
  `criado_em` TEXT,
  FOREIGN KEY (`agendamento_id`) REFERENCES `agendamentos` (`id`)
);;
CREATE TABLE `prestadores_servico` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `usuario_id` INTEGER NOT NULL,
  `categoria` TEXT NOT NULL,
  `especialidade` TEXT NOT NULL,
  `descricao` TEXT,
  `experiencia` INTEGER,
  `valor_hora` REAL,
  `disponivel` TEXT,
  `taxa_plataforma` REAL,
  `raio_atuacao` INTEGER,
  `disponivel_online` INTEGER,
  `verificado` INTEGER,
  `saldo_disponivel` REAL,
  `total_ganho` REAL,
  `categoria_id` INTEGER,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`categoria_id`) REFERENCES `categorias_servico` (`id`)
);;
INSERT INTO "prestadores_servico" VALUES(1,1,'cozinheiro','Culinária Internacional','Profissional qualificado em Culinária Internacional com anos de experiência servindo a comunidade moçambicana.',6,940.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(2,2,'cozinheiro','Doces e Sobremesas','Profissional qualificado em Doces e Sobremesas com anos de experiência servindo a comunidade moçambicana.',15,882.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(3,3,'consultor','TI','Profissional qualificado em TI com anos de experiência servindo a comunidade moçambicana.',4,1213.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(4,4,'cozinheiro','Doces e Sobremesas','Profissional qualificado em Doces e Sobremesas com anos de experiência servindo a comunidade moçambicana.',8,1832.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(5,5,'advogado','Direito Civil','Profissional qualificado em Direito Civil com anos de experiência servindo a comunidade moçambicana.',4,1224.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(6,6,'personal_trainer','Condicionamento Físico','Profissional qualificado em Condicionamento Físico com anos de experiência servindo a comunidade moçambicana.',2,734.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(7,7,'cozinheiro','Doces e Sobremesas','Profissional qualificado em Doces e Sobremesas com anos de experiência servindo a comunidade moçambicana.',15,2064.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(8,8,'consultor','Marketing Digital','Profissional qualificado em Marketing Digital com anos de experiência servindo a comunidade moçambicana.',3,1007.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(9,9,'cozinheiro','Doces e Sobremesas','Profissional qualificado em Doces e Sobremesas com anos de experiência servindo a comunidade moçambicana.',9,2354.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(10,10,'advogado','Direito Civil','Profissional qualificado em Direito Civil com anos de experiência servindo a comunidade moçambicana.',7,2381.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(11,11,'advogado','Direito Trabalhista','Profissional qualificado em Direito Trabalhista com anos de experiência servindo a comunidade moçambicana.',11,1581.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(12,12,'advogado','Direito Trabalhista','Profissional qualificado em Direito Trabalhista com anos de experiência servindo a comunidade moçambicana.',7,1817.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
INSERT INTO "prestadores_servico" VALUES(13,14,'','Pastor',NULL,0,0.0,'sim',10.0,10,0,0,0.0,0.0,NULL);;
CREATE TABLE `servicos` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `prestador_id` INTEGER NOT NULL,
  `titulo` TEXT NOT NULL,
  `descricao` TEXT NOT NULL,
  `nivel` TEXT NOT NULL,
  `duracao` INTEGER,
  `preco` REAL NOT NULL,
  `tags` TEXT,
  `ativo` INTEGER,
  FOREIGN KEY (`prestador_id`) REFERENCES `prestadores_servico` (`id`)
);;
INSERT INTO "servicos" VALUES(1,1,'Serviço de Culinária Internacional - Básico','Serviço profissional de Culinária Internacional com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',30,940.0,NULL,1);;
INSERT INTO "servicos" VALUES(2,2,'Serviço de Doces e Sobremesas - Básico','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',90,2646.0,NULL,1);;
INSERT INTO "servicos" VALUES(3,2,'Serviço de Doces e Sobremesas - Intermediário','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',30,882.0,NULL,1);;
INSERT INTO "servicos" VALUES(4,2,'Serviço de Doces e Sobremesas - Avançado','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','avancado',90,1764.0,NULL,1);;
INSERT INTO "servicos" VALUES(5,3,'Serviço de TI - Básico','Serviço profissional de TI com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',60,1213.0,NULL,1);;
INSERT INTO "servicos" VALUES(6,4,'Serviço de Doces e Sobremesas - Básico','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',90,5496.0,NULL,1);;
INSERT INTO "servicos" VALUES(7,5,'Serviço de Direito Civil - Básico','Serviço profissional de Direito Civil com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',60,4896.0,NULL,1);;
INSERT INTO "servicos" VALUES(8,5,'Serviço de Direito Civil - Intermediário','Serviço profissional de Direito Civil com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',30,3672.0,NULL,1);;
INSERT INTO "servicos" VALUES(9,6,'Serviço de Condicionamento Físico - Básico','Serviço profissional de Condicionamento Físico com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',120,2202.0,NULL,1);;
INSERT INTO "servicos" VALUES(10,7,'Serviço de Doces e Sobremesas - Básico','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',30,6192.0,NULL,1);;
INSERT INTO "servicos" VALUES(11,7,'Serviço de Doces e Sobremesas - Intermediário','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',90,2064.0,NULL,1);;
INSERT INTO "servicos" VALUES(12,8,'Serviço de Marketing Digital - Básico','Serviço profissional de Marketing Digital com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',30,2014.0,NULL,1);;
INSERT INTO "servicos" VALUES(13,8,'Serviço de Marketing Digital - Intermediário','Serviço profissional de Marketing Digital com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',90,2014.0,NULL,1);;
INSERT INTO "servicos" VALUES(14,8,'Serviço de Marketing Digital - Avançado','Serviço profissional de Marketing Digital com qualidade garantida. Atendimento personalizado para suas necessidades.','avancado',30,1007.0,NULL,1);;
INSERT INTO "servicos" VALUES(15,9,'Serviço de Doces e Sobremesas - Básico','Serviço profissional de Doces e Sobremesas com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',60,2354.0,NULL,1);;
INSERT INTO "servicos" VALUES(16,10,'Serviço de Direito Civil - Básico','Serviço profissional de Direito Civil com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',120,7143.0,NULL,1);;
INSERT INTO "servicos" VALUES(17,11,'Serviço de Direito Trabalhista - Básico','Serviço profissional de Direito Trabalhista com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',120,6324.0,NULL,1);;
INSERT INTO "servicos" VALUES(18,11,'Serviço de Direito Trabalhista - Intermediário','Serviço profissional de Direito Trabalhista com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',30,4743.0,NULL,1);;
INSERT INTO "servicos" VALUES(19,11,'Serviço de Direito Trabalhista - Avançado','Serviço profissional de Direito Trabalhista com qualidade garantida. Atendimento personalizado para suas necessidades.','avancado',90,3162.0,NULL,1);;
INSERT INTO "servicos" VALUES(20,12,'Serviço de Direito Trabalhista - Básico','Serviço profissional de Direito Trabalhista com qualidade garantida. Atendimento personalizado para suas necessidades.','basico',90,5451.0,NULL,1);;
INSERT INTO "servicos" VALUES(21,12,'Serviço de Direito Trabalhista - Intermediário','Serviço profissional de Direito Trabalhista com qualidade garantida. Atendimento personalizado para suas necessidades.','intermediario',90,5451.0,NULL,1);;
CREATE TABLE `tickets_respostas` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `ticket_id` INTEGER NOT NULL,
  `usuario_id` INTEGER NOT NULL,
  `resposta` TEXT NOT NULL,
  `data_resposta` TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`ticket_id`) REFERENCES `tickets_suporte` (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
);;
INSERT INTO "tickets_respostas" VALUES(1,3,15,'Trabalhando nisso...','2025-11-05 06:36:11');;
INSERT INTO "tickets_respostas" VALUES(2,3,15,'quase resolvido','2025-11-05 06:50:13');;
CREATE TABLE `tickets_suporte` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `usuario_id` INTEGER,
  `assunto` TEXT,
  `descricao` TEXT,
  `categoria` TEXT,
  `status` TEXT,
  `prioridade` TEXT,
  `data_abertura` TEXT,
  `data_resolucao` TEXT,
  `resolucao` TEXT,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
);;
INSERT INTO "tickets_suporte" VALUES(1,13,'Nao meu chat nao funciona','Chat nao funciona','tecnico','aberto','alta','2025-11-04 23:39:13',NULL,NULL);;
INSERT INTO "tickets_suporte" VALUES(2,1,'Pagamentos','Como fazer pagamentos','financeiro','fechado','alta','2025-11-04 23:40:49','2025-11-04 23:43:35',NULL);;
INSERT INTO "tickets_suporte" VALUES(3,1,'Pagamentos','kgjg','financeiro','em_andamento','urgente','2025-11-04 23:45:31',NULL,NULL);;
CREATE TABLE `transacoes_financeiras` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `usuario_id` INTEGER,
  `prestador_id` INTEGER,
  `tipo` TEXT,
  `valor` REAL,
  `descricao` TEXT,
  `saldo_anterior` REAL,
  `saldo_posterior` REAL,
  `referencia` TEXT,
  `data_transacao` TEXT,
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  FOREIGN KEY (`prestador_id`) REFERENCES `prestadores_servico` (`id`)
);;
CREATE TABLE `usuario` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nome` TEXT NOT NULL,
  `email` TEXT NOT NULL,
  `senha_hash` TEXT,
  `tipo` TEXT,
  `data_cadastro` TEXT,
  UNIQUE (`email`)
);;
CREATE TABLE `usuarios` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `nome` TEXT NOT NULL,
  `email` TEXT NOT NULL,
  `senha_hash` TEXT NOT NULL,
  `tipo` TEXT,
  `telefone` TEXT,
  `cidade` TEXT,
  `bairro` TEXT,
  `coordenadas` TEXT,
  `avatar_url` TEXT,
  `data_cadastro` TEXT,
  `ultimo_login` TEXT,
  `ativo` INTEGER,
  UNIQUE (`email`)
);;
INSERT INTO "usuarios" VALUES(1,'João Maputo','prestador0@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:24',NULL,1);;
INSERT INTO "usuarios" VALUES(2,'Maria Matola','prestador1@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:24',NULL,1);;
INSERT INTO "usuarios" VALUES(3,'Carlos Beira','prestador2@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:24',NULL,1);;
INSERT INTO "usuarios" VALUES(4,'Ana Nampula','prestador3@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:24',NULL,1);;
INSERT INTO "usuarios" VALUES(5,'José Quelimane','prestador4@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(6,'Teresa Tete','prestador5@servicos.co.mz','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(7,'Paulo Pemba','prestador6@servicos.co.mz','scrypt:32768:8:1$WtP9eqjk3T2GNAvl$fbd82324e36150a978a8e4d6020785e20a91a5f49553ecad8833fb9f647419a5aaf13b3badc0c4a56d4dbfa8de0ac5a05eac36b6655c249b2452b12ae6c624ee','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(8,'Luisa Inhambane','prestador7@servicos.co.mz','scrypt:32768:8:1$d3GE3rRUc8InTMwA$8e9096a6a9f02c01f0c3ff343d984d6cedf0b39ef679a8b18aa8e458f82d7927d93e0d41a3b250737b74265f726079981b2e10ad81af418d7ea558fcdc588f3c','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(9,'Miguel Xai-Xai','prestador8@servicos.co.mz','scrypt:32768:8:1$3UmjD7ToK70B7QFW$daf9c096cf55224fa7bbb490532c45fa93b63d5fee1794920950561dc9cdc4f57a98370d64b8f23a3e8de044897f722bb665b6f6015d50d1b31c158dc774e510','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(10,'Catarina Chimoio','prestador9@servicos.co.mz','scrypt:32768:8:1$kW33Qtj3PG1Ln7AQ$5b3964ef66e94a2e09d170c7b9da0a41fcefcbff8f7a078b3f06a3b67a5c21776d9f0db6509d0ebaa2147f0e41735f8442dd687bf5f95d299a1e9847126815f8','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(11,'António Lichinga','prestador10@servicos.co.mz','scrypt:32768:8:1$b50kC2AoSm3IJ614$e0c5cef30ce6b40fb297e0d4d2522699e61866c4cdb72f6dc1aafe49be8cf3c6c84cc2829d39f4daf49adb33882cd906887b5a5a59243d25debb32cdbc1c3d84','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:25',NULL,1);;
INSERT INTO "usuarios" VALUES(12,'Isabel Maxixe','prestador11@servicos.co.mz','scrypt:32768:8:1$ZPmJ1caFyAkeUV44$0b12abf50214e3861bb8025b523f7275319786afc862a2ee2a52be7f58d558e6d7530d2d28b33e148dc0bb72591804e5277c63a6d640d4a9bf3f804419eae40e','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-28 12:06:26',NULL,1);;
INSERT INTO "usuarios" VALUES(13,'Zayn Malik','nachingweyaa@gmail.com','scrypt:32768:8:1$2L3KLvFdZqY24dz4$02d7a4050ef12837f58c046c5e14fc1fc95ab176e4db287c672e4e032acab21db4c018784e6ffd35443fa9881db5f2e9103de94977ef9d8523da0d5fb733882e','cliente',NULL,NULL,NULL,NULL,NULL,'2025-10-30 21:53:33',NULL,1);;
INSERT INTO "usuarios" VALUES(14,'Mario Baule','nachingweyaaa@gmail.com','scrypt:32768:8:1$pGeMiKy6FnIlK70i$5e3273b77cc1eb6314196a530ba53313c6a0ae124d7d5946af3ced3a8b1251657ea73e9a3b41f2a9e705c8dde23cbb6a950fb72bfc578e7bd50001a37cac5282','prestador',NULL,NULL,NULL,NULL,NULL,'2025-10-30 23:21:28',NULL,1);;
INSERT INTO "usuarios" VALUES(15,'Administrador Sistema','admin@servicospro.mz','scrypt:32768:8:1$S9ygPjQgseD3h6Ld$b6a5e9e8c3da25914b23e0d6a394294ddfe3cb9de3f1bdf291dac2457125dc49c2a252d72205a30400fd6dd2319763447cf17fc52a4243084bc9ac882d177f5d','admin','+258841234567','Maputo','Centro',NULL,NULL,'2025-11-04 22:25:21',NULL,1);;
DELETE FROM "sqlite_sequence";;
INSERT INTO "sqlite_sequence" VALUES('usuarios',15);;
INSERT INTO "sqlite_sequence" VALUES('categorias_servico',6);;
INSERT INTO "sqlite_sequence" VALUES('prestadores_servico',13);;
INSERT INTO "sqlite_sequence" VALUES('servicos',21);;
INSERT INTO "sqlite_sequence" VALUES('agendamentos',1);;
INSERT INTO "sqlite_sequence" VALUES('avaliacoes',1);;
INSERT INTO "sqlite_sequence" VALUES('conversas',1);;
INSERT INTO "sqlite_sequence" VALUES('mensagens',10);;
INSERT INTO "sqlite_sequence" VALUES('notificacoes',23);;
INSERT INTO "sqlite_sequence" VALUES('tickets_suporte',3);;
INSERT INTO "sqlite_sequence" VALUES('tickets_respostas',2);;
COMMIT;;
