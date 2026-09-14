from datetime import date
import csv
from decimal import Decimal, InvalidOperation
from math import ceil

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import (
    Alerta, Atendimento, Auditoria, Cliente, Comissao, ConfiguracaoEmpresa,
    ContaFinanceira, Dimensionamento, DocumentoTecnico, Equipamento, Garantia,
    HistoricoEquipamento, Lead, Manutencao, MovimentoCaixa, Oportunidade,
    Orcamento, Projeto, SistemaEquipamento, SistemaSolar, Venda, VisitaTecnica,
)


def _decimal(value):
    try:
        return Decimal(value or '0')
    except (InvalidOperation, TypeError):
        return Decimal('0')


def _date(value, default=None):
    try:
        return date.fromisoformat(value) if value else default
    except ValueError:
        return default


def _cliente(value):
    return Cliente.objects.filter(pk=value).first() if value else None


@login_required
def inicio(request):
    clientes = Cliente.objects.all().order_by('-data_cadastro')

    return render(request, 'inicio.html', {
        'clientes': clientes,
        'total_clientes': clientes.count(),
    })


@login_required
def novo_cliente(request):
    if request.method == 'POST':
        Cliente.objects.create(
            nome=request.POST.get('nome', '').strip(),
            telefone=request.POST.get('telefone', '').strip(),
            email=request.POST.get('email', '').strip(),
            endereco=request.POST.get('endereco', '').strip(),
            documento=request.POST.get('documento', '').strip(),
        )

        return redirect('inicio')

    return render(request, 'novo_cliente.html')


@login_required
def comercial(request):
    return render(request, 'comercial_dashboard.html', {
        'total_leads': Lead.objects.count(),
        'total_oportunidades': Oportunidade.objects.exclude(etapa__in=[Oportunidade.Etapa.GANHA, Oportunidade.Etapa.PERDIDA]).count(),
        'total_visitas': VisitaTecnica.objects.filter(status=VisitaTecnica.Status.AGENDADA).count(),
        'total_orcamentos': Orcamento.objects.filter(status__in=[Orcamento.Status.RASCUNHO, Orcamento.Status.ENVIADO]).count(),
        'oportunidades': Oportunidade.objects.select_related('cliente', 'lead')[:6],
    })


@login_required
def leads(request):
    return render(request, 'comercial_lista.html', {
        'titulo': 'Leads', 'eyebrow': 'Comercial', 'descricao': 'Potenciais clientes e novos contatos.',
        'acao_url': 'novo_lead', 'acao_label': 'Novo lead', 'tipo': 'leads',
        'leads': Lead.objects.select_related('responsavel').all(),
    })


@login_required
def novo_lead(request):
    if request.method == 'POST':
        Lead.objects.create(
            nome=request.POST.get('nome', '').strip(), telefone=request.POST.get('telefone', '').strip(),
            email=request.POST.get('email', '').strip(), cidade=request.POST.get('cidade', '').strip(),
            origem=request.POST.get('origem', Lead.Origem.OUTRO), interesse=request.POST.get('interesse', '').strip(),
            observacoes=request.POST.get('observacoes', '').strip(), responsavel=request.user,
        )
        return redirect('leads')
    return render(request, 'comercial_form.html', {'tipo': 'lead', 'titulo': 'Novo lead', 'eyebrow': 'Comercial', 'origens': Lead.Origem.choices})


@login_required
def oportunidades(request):
    return render(request, 'comercial_lista.html', {
        'titulo': 'CRM', 'eyebrow': 'Relacionamento', 'descricao': 'Acompanhe oportunidades ao longo do funil de vendas.',
        'acao_url': 'nova_oportunidade', 'acao_label': 'Nova oportunidade', 'tipo': 'oportunidades',
        'oportunidades': Oportunidade.objects.select_related('cliente', 'lead', 'responsavel').all(),
    })


@login_required
def nova_oportunidade(request):
    if request.method == 'POST':
        Oportunidade.objects.create(
            titulo=request.POST.get('titulo', '').strip(), cliente=_cliente(request.POST.get('cliente')),
            lead=Lead.objects.filter(pk=request.POST.get('lead')).first() if request.POST.get('lead') else None,
            etapa=request.POST.get('etapa', Oportunidade.Etapa.QUALIFICACAO), valor_estimado=_decimal(request.POST.get('valor_estimado')),
            probabilidade=request.POST.get('probabilidade') or 10, data_prevista=_date(request.POST.get('data_prevista')),
            responsavel=request.user,
        )
        return redirect('oportunidades')
    return render(request, 'comercial_form.html', {
        'tipo': 'oportunidade', 'titulo': 'Nova oportunidade', 'eyebrow': 'CRM',
        'clientes': Cliente.objects.all(), 'leads': Lead.objects.all(), 'etapas': Oportunidade.Etapa.choices,
    })


@login_required
def visitas(request):
    return render(request, 'comercial_lista.html', {
        'titulo': 'Visitas técnicas', 'eyebrow': 'Operação comercial', 'descricao': 'Organize vistorias e levantamentos no local.',
        'acao_url': 'nova_visita', 'acao_label': 'Agendar visita', 'tipo': 'visitas',
        'visitas': VisitaTecnica.objects.select_related('cliente', 'lead', 'responsavel').all(),
    })


@login_required
def nova_visita(request):
    if request.method == 'POST':
        VisitaTecnica.objects.create(
            cliente=_cliente(request.POST.get('cliente')), lead=Lead.objects.filter(pk=request.POST.get('lead')).first() if request.POST.get('lead') else None,
            data_agendada=_date(request.POST.get('data_agendada'), timezone.localdate()), horario=request.POST.get('horario') or None,
            endereco=request.POST.get('endereco', '').strip(), observacoes=request.POST.get('observacoes', '').strip(), responsavel=request.user,
        )
        return redirect('visitas')
    return render(request, 'comercial_form.html', {
        'tipo': 'visita', 'titulo': 'Agendar visita técnica', 'eyebrow': 'Operação comercial',
        'clientes': Cliente.objects.all(), 'leads': Lead.objects.all(),
    })


@login_required
def orcamentos(request):
    return render(request, 'comercial_lista.html', {
        'titulo': 'Orçamentos', 'eyebrow': 'Propostas comerciais', 'descricao': 'Crie e acompanhe propostas para seus clientes.',
        'acao_url': 'novo_orcamento', 'acao_label': 'Novo orçamento', 'tipo': 'orcamentos',
        'orcamentos': Orcamento.objects.select_related('cliente', 'responsavel').all(),
    })


@login_required
def novo_orcamento(request):
    if request.method == 'POST':
        Orcamento.objects.create(
            cliente=_cliente(request.POST.get('cliente')), descricao=request.POST.get('descricao', '').strip(),
            valor_total=_decimal(request.POST.get('valor_total')), validade=_date(request.POST.get('validade')),
            status=request.POST.get('status', Orcamento.Status.RASCUNHO), responsavel=request.user,
        )
        return redirect('orcamentos')
    return render(request, 'comercial_form.html', {
        'tipo': 'orcamento', 'titulo': 'Novo orçamento', 'eyebrow': 'Propostas comerciais',
        'clientes': Cliente.objects.all(), 'status_orcamento': Orcamento.Status.choices,
    })


@login_required
def vendas(request):
    return render(request, 'comercial_lista.html', {
        'titulo': 'Vendas', 'eyebrow': 'Comercial', 'descricao': 'Negócios fechados e em implantação.',
        'acao_url': 'nova_venda', 'acao_label': 'Registrar venda', 'tipo': 'vendas',
        'vendas': Venda.objects.select_related('cliente', 'orcamento').all(),
    })


@login_required
def nova_venda(request):
    if request.method == 'POST':
        Venda.objects.create(
            cliente=_cliente(request.POST.get('cliente')), valor_total=_decimal(request.POST.get('valor_total')),
            status=request.POST.get('status', Venda.Status.EM_IMPLANTACAO),
        )
        return redirect('vendas')
    return render(request, 'comercial_form.html', {
        'tipo': 'venda', 'titulo': 'Registrar venda', 'eyebrow': 'Comercial',
        'clientes': Cliente.objects.all(), 'status_venda': Venda.Status.choices,
    })


@login_required
def engenharia(request):
    return render(request, 'engenharia_dashboard.html', {
        'total_projetos': Projeto.objects.count(),
        'total_dimensionamentos': Dimensionamento.objects.count(),
        'total_sistemas': SistemaSolar.objects.count(),
        'total_equipamentos': Equipamento.objects.filter(ativo=True).count(),
        'projetos': Projeto.objects.select_related('cliente', 'responsavel')[:6],
    })


@login_required
def projetos(request):
    return render(request, 'engenharia_lista.html', {
        'tipo': 'projetos', 'titulo': 'Projetos', 'eyebrow': 'Engenharia',
        'descricao': 'Organize projetos fotovoltaicos do planejamento à instalação.',
        'acao_url': 'novo_projeto', 'acao_label': 'Novo projeto',
        'projetos': Projeto.objects.select_related('cliente', 'responsavel').all(),
    })


@login_required
def novo_projeto(request):
    if request.method == 'POST':
        Projeto.objects.create(
            nome=request.POST.get('nome', '').strip(), cliente=_cliente(request.POST.get('cliente')),
            oportunidade=Oportunidade.objects.filter(pk=request.POST.get('oportunidade')).first() if request.POST.get('oportunidade') else None,
            status=request.POST.get('status', Projeto.Status.PLANEJAMENTO),
            endereco_instalacao=request.POST.get('endereco_instalacao', '').strip(), responsavel=request.user,
        )
        return redirect('projetos')
    return render(request, 'engenharia_form.html', {
        'tipo': 'projeto', 'titulo': 'Novo projeto', 'eyebrow': 'Engenharia',
        'clientes': Cliente.objects.all(), 'oportunidades': Oportunidade.objects.all(), 'status_projeto': Projeto.Status.choices,
    })


@login_required
def dimensionamentos(request):
    return render(request, 'engenharia_lista.html', {
        'tipo': 'dimensionamentos', 'titulo': 'Dimensionamentos', 'eyebrow': 'Engenharia',
        'descricao': 'Memórias de cálculo e premissas energéticas dos projetos.',
        'acao_url': 'novo_dimensionamento', 'acao_label': 'Novo dimensionamento',
        'dimensionamentos': Dimensionamento.objects.select_related('projeto', 'projeto__cliente').all(),
    })


@login_required
def novo_dimensionamento(request):
    if request.method == 'POST':
        consumo = _decimal(request.POST.get('consumo_medio_kwh'))
        irradiacao = _decimal(request.POST.get('irradiacao_media'))
        fator = _decimal(request.POST.get('fator_performance') or '0.80')
        potencia = _decimal(request.POST.get('potencia_calculada_kwp'))
        if not potencia and irradiacao and fator:
            potencia = (consumo / (irradiacao * Decimal('30') * fator)).quantize(Decimal('0.01'))
        modulo = int(request.POST.get('potencia_modulo_wp') or 0)
        quantidade = int(request.POST.get('quantidade_modulos') or (ceil(float(potencia * 1000 / modulo)) if potencia and modulo else 0))
        Dimensionamento.objects.update_or_create(
            projeto_id=request.POST.get('projeto'), defaults={
                'consumo_medio_kwh': consumo, 'irradiacao_media': irradiacao, 'fator_performance': fator,
                'potencia_calculada_kwp': potencia, 'quantidade_modulos': quantidade, 'potencia_modulo_wp': modulo,
                'potencia_inversor_kw': _decimal(request.POST.get('potencia_inversor_kw')),
                'geracao_estimada_anual_kwh': _decimal(request.POST.get('geracao_estimada_anual_kwh')),
                'area_necessaria_m2': _decimal(request.POST.get('area_necessaria_m2')),
                'observacoes': request.POST.get('observacoes', '').strip(),
            },
        )
        return redirect('dimensionamentos')
    return render(request, 'engenharia_form.html', {
        'tipo': 'dimensionamento', 'titulo': 'Novo dimensionamento', 'eyebrow': 'Engenharia',
        'projetos': Projeto.objects.all(),
    })


@login_required
def sistemas(request):
    return render(request, 'engenharia_lista.html', {
        'tipo': 'sistemas', 'titulo': 'Sistemas solares', 'eyebrow': 'Engenharia',
        'descricao': 'Sistemas fotovoltaicos e seus equipamentos instalados.',
        'acao_url': 'novo_sistema', 'acao_label': 'Novo sistema',
        'sistemas': SistemaSolar.objects.select_related('projeto', 'projeto__cliente').prefetch_related('equipamentos').all(),
    })


@login_required
def novo_sistema(request):
    if request.method == 'POST':
        sistema = SistemaSolar.objects.create(
            projeto_id=request.POST.get('projeto'), nome=request.POST.get('nome', '').strip(),
            potencia_kwp=_decimal(request.POST.get('potencia_kwp')), status=request.POST.get('status', SistemaSolar.Status.PLANEJAMENTO),
            data_instalacao=_date(request.POST.get('data_instalacao')), observacoes=request.POST.get('observacoes', '').strip(),
        )
        if request.POST.get('equipamento'):
            SistemaEquipamento.objects.create(sistema=sistema, equipamento_id=request.POST['equipamento'], quantidade=int(request.POST.get('quantidade') or 1))
        return redirect('sistemas')
    return render(request, 'engenharia_form.html', {
        'tipo': 'sistema', 'titulo': 'Novo sistema solar', 'eyebrow': 'Engenharia',
        'projetos': Projeto.objects.all(), 'equipamentos': Equipamento.objects.filter(ativo=True), 'status_sistema': SistemaSolar.Status.choices,
    })


@login_required
def equipamentos(request):
    return render(request, 'engenharia_lista.html', {
        'tipo': 'equipamentos', 'titulo': 'Equipamentos', 'eyebrow': 'Catálogo técnico',
        'descricao': 'Módulos, inversores, estruturas e componentes disponíveis.',
        'acao_url': 'novo_equipamento', 'acao_label': 'Novo equipamento',
        'equipamentos': Equipamento.objects.all(),
    })


@login_required
def novo_equipamento(request):
    if request.method == 'POST':
        Equipamento.objects.create(
            nome=request.POST.get('nome', '').strip(), categoria=request.POST.get('categoria', Equipamento.Categoria.OUTRO),
            fabricante=request.POST.get('fabricante', '').strip(), modelo=request.POST.get('modelo', '').strip(),
            potencia_nominal=_decimal(request.POST.get('potencia_nominal')), unidade=request.POST.get('unidade', 'unidade').strip() or 'unidade',
        )
        return redirect('equipamentos')
    return render(request, 'engenharia_form.html', {
        'tipo': 'equipamento', 'titulo': 'Novo equipamento', 'eyebrow': 'Catálogo técnico', 'categorias': Equipamento.Categoria.choices,
    })


@login_required
def documentos(request):
    return render(request, 'engenharia_lista.html', {
        'tipo': 'documentos', 'titulo': 'Documentação técnica', 'eyebrow': 'Engenharia',
        'descricao': 'Controle versões e arquivos técnicos de cada projeto.',
        'acao_url': 'novo_documento', 'acao_label': 'Adicionar documento',
        'documentos': DocumentoTecnico.objects.select_related('projeto', 'criado_por').all(),
    })


@login_required
def novo_documento(request):
    if request.method == 'POST':
        DocumentoTecnico.objects.create(
            projeto_id=request.POST.get('projeto'), titulo=request.POST.get('titulo', '').strip(),
            tipo=request.POST.get('tipo', DocumentoTecnico.Tipo.OUTRO), versao=request.POST.get('versao', '1.0').strip() or '1.0',
            descricao=request.POST.get('descricao', '').strip(), arquivo=request.FILES.get('arquivo'), criado_por=request.user,
        )
        return redirect('documentos')
    return render(request, 'engenharia_form.html', {
        'tipo': 'documento', 'titulo': 'Adicionar documento técnico', 'eyebrow': 'Engenharia',
        'projetos': Projeto.objects.all(), 'tipos_documento': DocumentoTecnico.Tipo.choices,
    })


@login_required
def gestao(request):
    contas_receber = ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.RECEBER)
    contas_pagar = ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.PAGAR)
    entradas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.ENTRADA)
    saidas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.SAIDA)
    return render(request, 'gestao_dashboard.html', {
        'clientes': Cliente.objects.count(), 'leads': Lead.objects.count(), 'projetos': Projeto.objects.count(),
        'sistemas': SistemaSolar.objects.count(), 'atendimentos': Atendimento.objects.exclude(status__in=[Atendimento.Status.RESOLVIDO, Atendimento.Status.CANCELADO]).count(),
        'alertas': Alerta.objects.exclude(status=Alerta.Status.RESOLVIDO).count(),
        'receber': _total(contas_receber.filter(status__in=[ContaFinanceira.Status.PENDENTE, ContaFinanceira.Status.ATRASADA])),
        'pagar': _total(contas_pagar.filter(status__in=[ContaFinanceira.Status.PENDENTE, ContaFinanceira.Status.ATRASADA])),
        'saldo': _total(entradas) - _total(saidas),
        'auditorias': Auditoria.objects.select_related('usuario')[:8],
    })


@login_required
def relatorios(request):
    return render(request, 'relatorios.html', {
        'total_clientes': Cliente.objects.count(), 'total_projetos': Projeto.objects.count(),
        'total_vendas': _total(Venda.objects.all(), 'valor_total'), 'total_atendimentos': Atendimento.objects.count(),
    })


@login_required
def exportar_relatorio(request):
    tipo = request.GET.get('tipo', 'clientes')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write('\ufeff')
    response['Content-Disposition'] = f'attachment; filename="solar-gest-{tipo}.csv"'
    writer = csv.writer(response)
    if tipo == 'financeiro':
        writer.writerow(['Tipo', 'Descrição', 'Valor', 'Vencimento', 'Status'])
        for item in ContaFinanceira.objects.all():
            writer.writerow([item.get_tipo_display(), item.descricao, item.valor, item.vencimento, item.get_status_display()])
    elif tipo == 'projetos':
        writer.writerow(['Código', 'Projeto', 'Cliente', 'Status'])
        for item in Projeto.objects.select_related('cliente'):
            writer.writerow([item.codigo, item.nome, item.cliente.nome, item.get_status_display()])
    elif tipo == 'atendimentos':
        writer.writerow(['Assunto', 'Cliente', 'Canal', 'Status', 'Criado em'])
        for item in Atendimento.objects.select_related('cliente'):
            writer.writerow([item.assunto, item.cliente.nome, item.get_canal_display(), item.get_status_display(), item.criado_em])
    else:
        writer.writerow(['Nome', 'E-mail', 'Telefone', 'Documento', 'Cadastro'])
        for item in Cliente.objects.all():
            writer.writerow([item.nome, item.email, item.telefone, item.documento, item.data_cadastro])
    return response


@login_required
def auditoria(request):
    return render(request, 'auditoria.html', {'auditorias': Auditoria.objects.select_related('usuario').all()[:200]})


@login_required
def configuracoes(request):
    config, _ = ConfiguracaoEmpresa.objects.get_or_create(pk=1)
    if request.method == 'POST':
        config.nome = request.POST.get('nome', '').strip() or 'Solar Gest'
        config.cnpj = request.POST.get('cnpj', '').strip()
        config.email = request.POST.get('email', '').strip()
        config.telefone = request.POST.get('telefone', '').strip()
        config.endereco = request.POST.get('endereco', '').strip()
        config.moeda = request.POST.get('moeda', 'BRL').strip() or 'BRL'
        config.save()
        return redirect('configuracoes')
    return render(request, 'configuracoes.html', {'config': config})


def _total(queryset, campo='valor'):
    return queryset.aggregate(total=Sum(campo))['total'] or Decimal('0')


def _sincronizar_movimento(conta, usuario):
    if conta.status == ContaFinanceira.Status.PAGA:
        MovimentoCaixa.objects.update_or_create(
            conta=conta,
            defaults={
                'tipo': MovimentoCaixa.Tipo.ENTRADA if conta.tipo == ContaFinanceira.Tipo.RECEBER else MovimentoCaixa.Tipo.SAIDA,
                'descricao': conta.descricao, 'valor': conta.valor,
                'data_movimento': conta.data_pagamento or conta.vencimento, 'criado_por': usuario,
            },
        )
    else:
        MovimentoCaixa.objects.filter(conta=conta).delete()


@login_required
def financeiro(request):
    contas_pagar = ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.PAGAR, status__in=[ContaFinanceira.Status.PENDENTE, ContaFinanceira.Status.ATRASADA])
    contas_receber = ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.RECEBER, status__in=[ContaFinanceira.Status.PENDENTE, ContaFinanceira.Status.ATRASADA])
    entradas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.ENTRADA)
    saidas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.SAIDA)
    return render(request, 'financeiro_dashboard.html', {
        'total_pagar': _total(contas_pagar), 'total_receber': _total(contas_receber),
        'total_entradas': _total(entradas), 'total_saidas': _total(saidas),
        'saldo': _total(entradas) - _total(saidas),
        'comissoes_pendentes': _total(Comissao.objects.exclude(status=Comissao.Status.PAGA)),
        'contas': ContaFinanceira.objects.select_related('cliente', 'projeto').all()[:8],
    })


@login_required
def contas_pagar(request):
    return render(request, 'financeiro_lista.html', {
        'tipo': 'pagar', 'titulo': 'Contas a pagar', 'eyebrow': 'Financeiro',
        'descricao': 'Despesas, fornecedores e compromissos da operação.', 'acao_url': 'nova_conta_pagar', 'acao_label': 'Nova conta',
        'contas': ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.PAGAR).select_related('projeto').all(),
    })


@login_required
def contas_receber(request):
    return render(request, 'financeiro_lista.html', {
        'tipo': 'receber', 'titulo': 'Contas a receber', 'eyebrow': 'Financeiro',
        'descricao': 'Parcelas e recebimentos previstos de clientes.', 'acao_url': 'nova_conta_receber', 'acao_label': 'Nova conta',
        'contas': ContaFinanceira.objects.filter(tipo=ContaFinanceira.Tipo.RECEBER).select_related('cliente', 'projeto').all(),
    })


@login_required
def nova_conta(request, tipo):
    if request.method == 'POST':
        conta = ContaFinanceira.objects.create(
            tipo=tipo, descricao=request.POST.get('descricao', '').strip(), categoria=request.POST.get('categoria', '').strip() or 'Geral',
            valor=_decimal(request.POST.get('valor')), vencimento=_date(request.POST.get('vencimento'), timezone.localdate()),
            data_pagamento=_date(request.POST.get('data_pagamento')), status=request.POST.get('status', ContaFinanceira.Status.PENDENTE),
            cliente=_cliente(request.POST.get('cliente')), fornecedor=request.POST.get('fornecedor', '').strip(),
            projeto=Projeto.objects.filter(pk=request.POST.get('projeto')).first() if request.POST.get('projeto') else None,
            observacoes=request.POST.get('observacoes', '').strip(), criado_por=request.user,
        )
        _sincronizar_movimento(conta, request.user)
        return redirect('contas_pagar' if tipo == ContaFinanceira.Tipo.PAGAR else 'contas_receber')
    return render(request, 'financeiro_form.html', {
        'tipo': tipo, 'titulo': 'Nova conta a pagar' if tipo == ContaFinanceira.Tipo.PAGAR else 'Nova conta a receber',
        'eyebrow': 'Financeiro', 'clientes': Cliente.objects.all(), 'projetos': Projeto.objects.all(), 'status_conta': ContaFinanceira.Status.choices,
    })


@login_required
def nova_conta_pagar(request):
    return nova_conta(request, ContaFinanceira.Tipo.PAGAR)


@login_required
def nova_conta_receber(request):
    return nova_conta(request, ContaFinanceira.Tipo.RECEBER)


@login_required
def fluxo_caixa(request):
    entradas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.ENTRADA)
    saidas = MovimentoCaixa.objects.filter(tipo=MovimentoCaixa.Tipo.SAIDA)
    return render(request, 'financeiro_lista.html', {
        'tipo': 'caixa', 'titulo': 'Fluxo de caixa', 'eyebrow': 'Financeiro',
        'descricao': 'Movimentações efetivamente realizadas no caixa.', 'acao_url': 'nova_conta_receber', 'acao_label': 'Lançar recebimento',
        'movimentos': MovimentoCaixa.objects.select_related('conta').all(), 'entradas': _total(entradas), 'saidas': _total(saidas),
    })


@login_required
def comissoes(request):
    return render(request, 'financeiro_lista.html', {
        'tipo': 'comissoes', 'titulo': 'Comissões', 'eyebrow': 'Financeiro',
        'descricao': 'Valores de comissão por venda e vendedor.', 'acao_url': 'nova_comissao', 'acao_label': 'Nova comissão',
        'comissoes': Comissao.objects.select_related('venda__cliente', 'vendedor').all(),
    })


@login_required
def nova_comissao(request):
    if request.method == 'POST':
        venda = Venda.objects.get(pk=request.POST.get('venda'))
        base = _decimal(request.POST.get('base_calculo')) or venda.valor_total
        percentual = _decimal(request.POST.get('percentual'))
        valor = _decimal(request.POST.get('valor')) or (base * percentual / Decimal('100')).quantize(Decimal('0.01'))
        Comissao.objects.create(
            venda=venda, vendedor=User.objects.get(pk=request.POST.get('vendedor')), percentual=percentual,
            base_calculo=base, valor=valor, status=request.POST.get('status', Comissao.Status.PENDENTE),
            data_pagamento=_date(request.POST.get('data_pagamento')), observacoes=request.POST.get('observacoes', '').strip(),
        )
        return redirect('comissoes')
    return render(request, 'financeiro_form.html', {
        'tipo': 'comissao', 'titulo': 'Nova comissão', 'eyebrow': 'Financeiro', 'vendas': Venda.objects.select_related('cliente').all(),
        'usuarios': User.objects.filter(is_active=True).order_by('username'), 'status_comissao': Comissao.Status.choices,
    })
