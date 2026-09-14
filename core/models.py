import uuid

from django.db import models
from django.contrib.auth.models import User


def gerar_codigo_orcamento():
    return f'ORC-{uuid.uuid4().hex[:8].upper()}'


def gerar_codigo_projeto():
    return f'PRJ-{uuid.uuid4().hex[:8].upper()}'


class PerfilUsuario(models.Model):
    class Cargo(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        GESTOR = 'gestor', 'Gestor'
        VENDEDOR = 'vendedor', 'Vendedor'
        TECNICO = 'tecnico', 'Técnico'

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField(max_length=20, choices=Cargo.choices, default=Cargo.VENDEDOR)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuário'
        verbose_name_plural = 'Perfis de usuários'

    def __str__(self):
        return f'{self.usuario.get_full_name() or self.usuario.username} - {self.get_cargo_display()}'


class Cliente(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=250, blank=True)
    documento = models.CharField(max_length=30, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Lead(models.Model):
    class Status(models.TextChoices):
        NOVO = 'novo', 'Novo'
        EM_CONTATO = 'em_contato', 'Em contato'
        QUALIFICADO = 'qualificado', 'Qualificado'
        CONVERTIDO = 'convertido', 'Convertido'
        PERDIDO = 'perdido', 'Perdido'

    class Origem(models.TextChoices):
        SITE = 'site', 'Site'
        INDICACAO = 'indicacao', 'Indicação'
        INSTAGRAM = 'instagram', 'Instagram'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        OUTRO = 'outro', 'Outro'

    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    origem = models.CharField(max_length=20, choices=Origem.choices, default=Origem.OUTRO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOVO)
    interesse = models.CharField(max_length=150, blank=True)
    observacoes = models.TextField(blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return self.nome


class Oportunidade(models.Model):
    class Etapa(models.TextChoices):
        QUALIFICACAO = 'qualificacao', 'Qualificação'
        VISITA = 'visita', 'Visita técnica'
        PROPOSTA = 'proposta', 'Proposta enviada'
        NEGOCIACAO = 'negociacao', 'Negociação'
        GANHA = 'ganha', 'Ganha'
        PERDIDA = 'perdida', 'Perdida'

    titulo = models.CharField(max_length=180)
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='oportunidades')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='oportunidades')
    etapa = models.CharField(max_length=20, choices=Etapa.choices, default=Etapa.QUALIFICACAO)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    probabilidade = models.PositiveSmallIntegerField(default=10)
    data_prevista = models.DateField(null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='oportunidades')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'
        ordering = ('-atualizado_em',)

    def __str__(self):
        return self.titulo


class VisitaTecnica(models.Model):
    class Status(models.TextChoices):
        AGENDADA = 'agendada', 'Agendada'
        REALIZADA = 'realizada', 'Realizada'
        CANCELADA = 'cancelada', 'Cancelada'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True, related_name='visitas_tecnicas')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_tecnicas')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='visitas_tecnicas')
    data_agendada = models.DateField()
    horario = models.TimeField(null=True, blank=True)
    endereco = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AGENDADA)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('data_agendada', 'horario')

    def __str__(self):
        nome = self.cliente or self.lead or 'Visita sem contato'
        return f'{nome} - {self.data_agendada:%d/%m/%Y}'


class Orcamento(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'rascunho', 'Rascunho'
        ENVIADO = 'enviado', 'Enviado'
        APROVADO = 'aprovado', 'Aprovado'
        RECUSADO = 'recusado', 'Recusado'
        EXPIRADO = 'expirado', 'Expirado'

    codigo = models.CharField(max_length=18, unique=True, default=gerar_codigo_orcamento)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='orcamentos')
    oportunidade = models.ForeignKey(Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    descricao = models.CharField(max_length=220)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    validade = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.RASCUNHO)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orcamentos')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return self.codigo


class Venda(models.Model):
    class Status(models.TextChoices):
        EM_IMPLANTACAO = 'em_implantacao', 'Em implantação'
        CONCLUIDA = 'concluida', 'Concluída'
        CANCELADA = 'cancelada', 'Cancelada'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vendas')
    oportunidade = models.OneToOneField(Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='venda')
    orcamento = models.OneToOneField(Orcamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='venda')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EM_IMPLANTACAO)
    data_venda = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('-data_venda',)

    def __str__(self):
        return f'Venda {self.cliente} - R$ {self.valor_total}'


class Projeto(models.Model):
    class Status(models.TextChoices):
        PLANEJAMENTO = 'planejamento', 'Planejamento'
        DIMENSIONAMENTO = 'dimensionamento', 'Dimensionamento'
        APROVADO = 'aprovado', 'Aprovado'
        EM_INSTALACAO = 'em_instalacao', 'Em instalação'
        CONCLUIDO = 'concluido', 'Concluído'
        PAUSADO = 'pausado', 'Pausado'

    codigo = models.CharField(max_length=18, unique=True, default=gerar_codigo_projeto)
    nome = models.CharField(max_length=180)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='projetos')
    oportunidade = models.ForeignKey(Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='projetos')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANEJAMENTO)
    endereco_instalacao = models.CharField(max_length=250, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='projetos')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class Dimensionamento(models.Model):
    projeto = models.OneToOneField(Projeto, on_delete=models.CASCADE, related_name='dimensionamento')
    consumo_medio_kwh = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    irradiacao_media = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text='kWh/m²/dia')
    fator_performance = models.DecimalField(max_digits=5, decimal_places=2, default=0.80)
    potencia_calculada_kwp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade_modulos = models.PositiveIntegerField(default=0)
    potencia_modulo_wp = models.PositiveIntegerField(default=0)
    potencia_inversor_kw = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    geracao_estimada_anual_kwh = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    area_necessaria_m2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacoes = models.TextField(blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Dimensionamento - {self.projeto.codigo}'


class Equipamento(models.Model):
    class Categoria(models.TextChoices):
        MODULO = 'modulo', 'Módulo fotovoltaico'
        INVERSOR = 'inversor', 'Inversor'
        ESTRUTURA = 'estrutura', 'Estrutura'
        PROTECAO = 'protecao', 'Proteção elétrica'
        OUTRO = 'outro', 'Outro'

    nome = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OUTRO)
    fabricante = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    potencia_nominal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidade = models.CharField(max_length=20, default='unidade')
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('categoria', 'nome')

    def __str__(self):
        return f'{self.nome} - {self.modelo}' if self.modelo else self.nome


class SistemaSolar(models.Model):
    class Status(models.TextChoices):
        PLANEJAMENTO = 'planejamento', 'Planejamento'
        EM_INSTALACAO = 'em_instalacao', 'Em instalação'
        OPERACIONAL = 'operacional', 'Operacional'
        MANUTENCAO = 'manutencao', 'Em manutenção'

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='sistemas_solares')
    nome = models.CharField(max_length=150)
    potencia_kwp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANEJAMENTO)
    data_instalacao = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    equipamentos = models.ManyToManyField(Equipamento, through='SistemaEquipamento', related_name='sistemas')

    def __str__(self):
        return f'{self.nome} - {self.projeto.codigo}'


class SistemaEquipamento(models.Model):
    sistema = models.ForeignKey(SistemaSolar, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('sistema', 'equipamento')


class DocumentoTecnico(models.Model):
    class Tipo(models.TextChoices):
        ART = 'art', 'ART / RRT'
        DIAGRAMA = 'diagrama', 'Diagrama elétrico'
        PLANTA = 'planta', 'Planta de instalação'
        MEMORIAL = 'memorial', 'Memorial descritivo'
        MANUAL = 'manual', 'Manual de equipamento'
        OUTRO = 'outro', 'Outro'

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='documentos_tecnicos')
    titulo = models.CharField(max_length=180)
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OUTRO)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to='documentacao_tecnica/', blank=True)
    versao = models.CharField(max_length=20, default='1.0')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return f'{self.titulo} - {self.projeto.codigo}'


class ContaFinanceira(models.Model):
    class Tipo(models.TextChoices):
        PAGAR = 'pagar', 'Conta a pagar'
        RECEBER = 'receber', 'Conta a receber'

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PAGA = 'paga', 'Paga'
        ATRASADA = 'atrasada', 'Atrasada'
        CANCELADA = 'cancelada', 'Cancelada'

    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    descricao = models.CharField(max_length=180)
    categoria = models.CharField(max_length=80, default='Geral')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_financeiras')
    fornecedor = models.CharField(max_length=150, blank=True)
    projeto = models.ForeignKey(Projeto, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_financeiras')
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_financeiras_criadas')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('vencimento', '-criado_em')

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.descricao}'


class MovimentoCaixa(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    descricao = models.CharField(max_length=180)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    data_movimento = models.DateField()
    conta = models.OneToOneField(ContaFinanceira, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimento_caixa')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimentos_caixa_criados')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-data_movimento', '-criado_em')

    def __str__(self):
        return f'{self.get_tipo_display()} - R$ {self.valor}'


class Comissao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADA = 'aprovada', 'Aprovada'
        PAGA = 'paga', 'Paga'

    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='comissoes')
    vendedor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comissoes')
    percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    base_calculo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    data_pagamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return f'Comissão de {self.vendedor} - R$ {self.valor}'


class Manutencao(models.Model):
    class Tipo(models.TextChoices):
        PREVENTIVA = 'preventiva', 'Preventiva'
        CORRETIVA = 'corretiva', 'Corretiva'

    class Status(models.TextChoices):
        ABERTA = 'aberta', 'Aberta'
        AGENDADA = 'agendada', 'Agendada'
        EM_EXECUCAO = 'em_execucao', 'Em execução'
        CONCLUIDA = 'concluida', 'Concluída'
        CANCELADA = 'cancelada', 'Cancelada'

    sistema = models.ForeignKey(SistemaSolar, on_delete=models.CASCADE, related_name='manutencoes')
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.CORRETIVA)
    titulo = models.CharField(max_length=180)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ABERTA)
    prioridade = models.CharField(max_length=12, default='normal')
    data_agendada = models.DateField(null=True, blank=True)
    data_conclusao = models.DateField(null=True, blank=True)
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='manutencoes')
    custo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('status', 'data_agendada', '-criado_em')

    def __str__(self):
        return f'{self.titulo} - {self.sistema}'


class Garantia(models.Model):
    class Status(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        EXPIRADA = 'expirada', 'Expirada'
        ACIONADA = 'acionada', 'Acionada'
        ENCERRADA = 'encerrada', 'Encerrada'

    sistema = models.ForeignKey(SistemaSolar, on_delete=models.CASCADE, related_name='garantias')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='garantias')
    titulo = models.CharField(max_length=180)
    inicio = models.DateField()
    fim = models.DateField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ATIVA)
    termos = models.TextField(blank=True)
    documento = models.FileField(upload_to='garantias/', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('fim', '-criado_em')

    def __str__(self):
        return f'{self.titulo} - {self.sistema}'


class HistoricoEquipamento(models.Model):
    class Evento(models.TextChoices):
        INSTALADO = 'instalado', 'Instalado'
        SUBSTITUIDO = 'substituido', 'Substituído'
        MANUTENCAO = 'manutencao', 'Manutenção'
        REMOVIDO = 'removido', 'Removido'

    sistema = models.ForeignKey(SistemaSolar, on_delete=models.CASCADE, related_name='historico_equipamentos')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.PROTECT, related_name='historico')
    evento = models.CharField(max_length=15, choices=Evento.choices)
    data_evento = models.DateField()
    numero_serie = models.CharField(max_length=100, blank=True)
    observacoes = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-data_evento', '-id')

    def __str__(self):
        return f'{self.equipamento} - {self.get_evento_display()}'


class Alerta(models.Model):
    class Nivel(models.TextChoices):
        INFO = 'info', 'Informativo'
        ATENCAO = 'atencao', 'Atenção'
        CRITICO = 'critico', 'Crítico'

    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        LIDO = 'lido', 'Lido'
        RESOLVIDO = 'resolvido', 'Resolvido'

    titulo = models.CharField(max_length=180)
    descricao = models.TextField(blank=True)
    nivel = models.CharField(max_length=10, choices=Nivel.choices, default=Nivel.INFO)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ABERTO)
    sistema = models.ForeignKey(SistemaSolar, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas')
    manutencao = models.ForeignKey(Manutencao, on_delete=models.CASCADE, null=True, blank=True, related_name='alertas')
    prazo = models.DateField(null=True, blank=True)
    resolvido_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('status', '-criado_em')

    def __str__(self):
        return self.titulo


class Atendimento(models.Model):
    class Canal(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEFONE = 'telefone', 'Telefone'
        EMAIL = 'email', 'E-mail'
        PORTAL = 'portal', 'Portal'
        OUTRO = 'outro', 'Outro'

    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ATENDIMENTO = 'em_atendimento', 'Em atendimento'
        AGUARDANDO_CLIENTE = 'aguardando_cliente', 'Aguardando cliente'
        RESOLVIDO = 'resolvido', 'Resolvido'
        CANCELADO = 'cancelado', 'Cancelado'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='atendimentos')
    sistema = models.ForeignKey(SistemaSolar, on_delete=models.SET_NULL, null=True, blank=True, related_name='atendimentos')
    assunto = models.CharField(max_length=180)
    descricao = models.TextField()
    canal = models.CharField(max_length=12, choices=Canal.choices, default=Canal.WHATSAPP)
    prioridade = models.CharField(max_length=12, default='normal')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTO)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='atendimentos')
    resolvido_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('status', '-criado_em')

    def __str__(self):
        return f'{self.assunto} - {self.cliente}'


class ConfiguracaoEmpresa(models.Model):
    nome = models.CharField(max_length=180, default='Solar Gest')
    cnpj = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    endereco = models.CharField(max_length=250, blank=True)
    moeda = models.CharField(max_length=5, default='BRL')
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração da empresa'
        verbose_name_plural = 'Configurações da empresa'

    def __str__(self):
        return self.nome


class Auditoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
    acao = models.CharField(max_length=20)
    rota = models.CharField(max_length=200)
    descricao = models.CharField(max_length=250, blank=True)
    metodo = models.CharField(max_length=10, default='GET')
    status_http = models.PositiveSmallIntegerField(default=200)
    ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-criado_em',)

    def __str__(self):
        return f'{self.acao} - {self.rota}'
