from django.contrib import admin
from .models import (
    Alerta, Atendimento, Auditoria, Cliente, Comissao, ConfiguracaoEmpresa,
    ContaFinanceira, Dimensionamento, DocumentoTecnico, Equipamento, Garantia,
    HistoricoEquipamento, Lead, Manutencao, MovimentoCaixa, Oportunidade,
    Orcamento, PerfilUsuario, Projeto, SistemaSolar, Venda, VisitaTecnica,
)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cargo', 'ativo', 'criado_em')
    list_filter = ('cargo', 'ativo')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'telefone',
        'email',
        'documento',
        'data_cadastro',
    )

    search_fields = (
        'nome',
        'telefone',
        'email',
        'documento',
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'origem', 'status', 'responsavel', 'criado_em')
    list_filter = ('status', 'origem')
    search_fields = ('nome', 'email', 'telefone', 'cidade')


@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'etapa', 'valor_estimado', 'probabilidade', 'responsavel')
    list_filter = ('etapa',)
    search_fields = ('titulo', 'cliente__nome', 'lead__nome')


@admin.register(VisitaTecnica)
class VisitaTecnicaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'lead', 'data_agendada', 'horario', 'status', 'responsavel')
    list_filter = ('status', 'data_agendada')


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'valor_total', 'status', 'validade', 'responsavel')
    list_filter = ('status',)
    search_fields = ('codigo', 'cliente__nome', 'descricao')


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'valor_total', 'status', 'data_venda')
    list_filter = ('status', 'data_venda')
    search_fields = ('cliente__nome',)


@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'cliente', 'status', 'responsavel', 'criado_em')
    list_filter = ('status',)
    search_fields = ('codigo', 'nome', 'cliente__nome')


@admin.register(Dimensionamento)
class DimensionamentoAdmin(admin.ModelAdmin):
    list_display = ('projeto', 'consumo_medio_kwh', 'potencia_calculada_kwp', 'quantidade_modulos', 'potencia_inversor_kw')
    search_fields = ('projeto__codigo', 'projeto__nome')


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'fabricante', 'modelo', 'potencia_nominal', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome', 'fabricante', 'modelo')


@admin.register(SistemaSolar)
class SistemaSolarAdmin(admin.ModelAdmin):
    list_display = ('nome', 'projeto', 'potencia_kwp', 'status', 'data_instalacao')
    list_filter = ('status',)
    search_fields = ('nome', 'projeto__codigo', 'projeto__nome')


@admin.register(DocumentoTecnico)
class DocumentoTecnicoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'projeto', 'tipo', 'versao', 'criado_por', 'criado_em')
    list_filter = ('tipo',)
    search_fields = ('titulo', 'projeto__codigo', 'projeto__nome')


@admin.register(ContaFinanceira)
class ContaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'categoria', 'valor', 'vencimento', 'status', 'cliente', 'fornecedor')
    list_filter = ('tipo', 'status', 'categoria')
    search_fields = ('descricao', 'categoria', 'cliente__nome', 'fornecedor')


@admin.register(MovimentoCaixa)
class MovimentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('data_movimento', 'tipo', 'descricao', 'valor', 'conta', 'criado_por')
    list_filter = ('tipo', 'data_movimento')
    search_fields = ('descricao',)


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'venda', 'percentual', 'base_calculo', 'valor', 'status', 'data_pagamento')
    list_filter = ('status', 'vendedor')
    search_fields = ('vendedor__username', 'vendedor__first_name', 'venda__cliente__nome')


@admin.register(ConfiguracaoEmpresa)
class ConfiguracaoEmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'telefone', 'atualizado_em')


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('criado_em', 'usuario', 'acao', 'rota', 'status_http', 'ip')
    list_filter = ('acao', 'status_http', 'criado_em')
    search_fields = ('rota', 'descricao', 'usuario__username', 'ip')
    readonly_fields = ('usuario', 'acao', 'rota', 'descricao', 'metodo', 'status_http', 'ip', 'criado_em')