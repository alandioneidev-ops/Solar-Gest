from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    comercial, inicio, leads, nova_venda, nova_visita, nova_oportunidade,
    novo_cliente, novo_lead, novo_orcamento, oportunidades, orcamentos,
    vendas, visitas,
)
from .views import (
    dimensionamentos, documentos, engenharia, equipamentos, novo_dimensionamento,
    novo_documento, novo_equipamento, novo_projeto, novo_sistema, projetos,
    sistemas,
)
from .views import (
    comissoes, contas_pagar, contas_receber, financeiro, fluxo_caixa,
    nova_comissao, nova_conta_pagar, nova_conta_receber,
)
from .views import auditoria, configuracoes, equipe, exportar_relatorio, gestao, relatorios, usinas


urlpatterns = [
    path("", inicio, name="inicio"),
    path("clientes/novo/", novo_cliente, name="novo_cliente"),
    path("comercial/", comercial, name="comercial"),
    path("comercial/leads/", leads, name="leads"),
    path("comercial/leads/novo/", novo_lead, name="novo_lead"),
    path("comercial/crm/", oportunidades, name="oportunidades"),
    path("comercial/crm/nova/", nova_oportunidade, name="nova_oportunidade"),
    path("comercial/visitas/", visitas, name="visitas"),
    path("comercial/visitas/nova/", nova_visita, name="nova_visita"),
    path("comercial/orcamentos/", orcamentos, name="orcamentos"),
    path("comercial/orcamentos/novo/", novo_orcamento, name="novo_orcamento"),
    path("comercial/vendas/", vendas, name="vendas"),
    path("comercial/vendas/nova/", nova_venda, name="nova_venda"),
    path("engenharia/", engenharia, name="engenharia"),
    path("engenharia/projetos/", projetos, name="projetos"),
    path("engenharia/projetos/novo/", novo_projeto, name="novo_projeto"),
    path("engenharia/dimensionamentos/", dimensionamentos, name="dimensionamentos"),
    path("engenharia/dimensionamentos/novo/", novo_dimensionamento, name="novo_dimensionamento"),
    path("engenharia/sistemas/", sistemas, name="sistemas"),
    path("engenharia/sistemas/novo/", novo_sistema, name="novo_sistema"),
    path("engenharia/equipamentos/", equipamentos, name="equipamentos"),
    path("engenharia/equipamentos/novo/", novo_equipamento, name="novo_equipamento"),
    path("engenharia/documentos/", documentos, name="documentos"),
    path("engenharia/documentos/novo/", novo_documento, name="novo_documento"),
    path("financeiro/", financeiro, name="financeiro"),
    path("financeiro/pagar/", contas_pagar, name="contas_pagar"),
    path("financeiro/pagar/nova/", nova_conta_pagar, name="nova_conta_pagar"),
    path("financeiro/receber/", contas_receber, name="contas_receber"),
    path("financeiro/receber/nova/", nova_conta_receber, name="nova_conta_receber"),
    path("financeiro/fluxo-de-caixa/", fluxo_caixa, name="fluxo_caixa"),
    path("financeiro/comissoes/", comissoes, name="comissoes"),
    path("financeiro/comissoes/nova/", nova_comissao, name="nova_comissao"),
    path("gestao/", gestao, name="gestao"),
    path("gestao/relatorios/", relatorios, name="relatorios"),
    path("gestao/relatorios/exportar/", exportar_relatorio, name="exportar_relatorio"),
    path("gestao/auditoria/", auditoria, name="auditoria"),
    path("gestao/configuracoes/", configuracoes, name="configuracoes"),
    path("usinas/", usinas, name="usinas"),
    path("equipe/", equipe, name="equipe"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]