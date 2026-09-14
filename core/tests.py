from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
	Auditoria, Cliente, ConfiguracaoEmpresa, ContaFinanceira, Dimensionamento,
	DocumentoTecnico, Equipamento, Lead, Oportunidade, Orcamento, PerfilUsuario,
	Projeto, SistemaSolar, Venda, VisitaTecnica,
)


class FundacaoTestCase(TestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(username='gestor', password='SenhaForte123!')

	def test_perfil_e_criado_para_novo_usuario(self):
		self.assertTrue(PerfilUsuario.objects.filter(usuario=self.usuario).exists())

	def test_dashboard_exige_autenticacao(self):
		resposta = self.client.get(reverse('inicio'))
		self.assertRedirects(resposta, f'{reverse("login")}?next={reverse("inicio")}')

	def test_usuario_autenticado_acessa_dashboard(self):
		self.client.login(username='gestor', password='SenhaForte123!')
		Cliente.objects.create(nome='Cliente de teste')

		resposta = self.client.get(reverse('inicio'))

		self.assertEqual(resposta.status_code, 200)
		self.assertContains(resposta, 'Cliente de teste')

	def test_usuario_autenticado_pode_cadastrar_cliente(self):
		self.client.login(username='gestor', password='SenhaForte123!')

		resposta = self.client.post(reverse('novo_cliente'), {'nome': 'Novo cliente'})

		self.assertRedirects(resposta, reverse('inicio'))
		self.assertTrue(Cliente.objects.filter(nome='Novo cliente').exists())

	def test_usuario_autenticado_pode_cadastrar_lead(self):
		self.client.login(username='gestor', password='SenhaForte123!')

		resposta = self.client.post(reverse('novo_lead'), {
			'nome': 'Lead Solar', 'telefone': '11999999999', 'origem': 'site',
			'interesse': 'Sistema de 10 kWp',
		})

		self.assertRedirects(resposta, reverse('leads'))
		self.assertTrue(Lead.objects.filter(nome='Lead Solar', responsavel=self.usuario).exists())

	def test_fluxo_comercial_cria_oportunidade_orcamento_e_venda(self):
		self.client.login(username='gestor', password='SenhaForte123!')
		cliente = Cliente.objects.create(nome='Cliente Comercial')

		self.client.post(reverse('nova_oportunidade'), {
			'titulo': 'Projeto fotovoltaico', 'cliente': cliente.pk, 'valor_estimado': '25000',
			'etapa': 'proposta', 'probabilidade': '70',
		})
		self.client.post(reverse('novo_orcamento'), {
			'cliente': cliente.pk, 'descricao': 'Sistema de 15 kWp', 'valor_total': '25000',
		})
		self.client.post(reverse('nova_venda'), {
			'cliente': cliente.pk, 'valor_total': '25000',
		})

		self.assertEqual(Oportunidade.objects.count(), 1)
		self.assertEqual(Orcamento.objects.count(), 1)
		self.assertEqual(Venda.objects.count(), 1)

	def test_paginas_comerciais_renderizam(self):
		self.client.login(username='gestor', password='SenhaForte123!')

		for nome_url in ('comercial', 'leads', 'oportunidades', 'visitas', 'orcamentos', 'vendas'):
			with self.subTest(nome_url=nome_url):
				resposta = self.client.get(reverse(nome_url))
				self.assertEqual(resposta.status_code, 200)

	def test_fluxo_de_engenharia(self):
		self.client.login(username='gestor', password='SenhaForte123!')
		cliente = Cliente.objects.create(nome='Cliente Engenharia')

		self.client.post(reverse('novo_projeto'), {
			'nome': 'Projeto Residencial', 'cliente': cliente.pk, 'endereco_instalacao': 'Rua Solar, 10',
		})
		projeto = Projeto.objects.get(nome='Projeto Residencial')

		self.client.post(reverse('novo_dimensionamento'), {
			'projeto': projeto.pk, 'consumo_medio_kwh': '600', 'irradiacao_media': '5',
			'fator_performance': '0.8', 'potencia_modulo_wp': '550',
		})
		dimensionamento = Dimensionamento.objects.get(projeto=projeto)
		self.assertEqual(dimensionamento.potencia_calculada_kwp, 5)
		self.assertEqual(dimensionamento.quantidade_modulos, 10)

		self.client.post(reverse('novo_equipamento'), {
			'nome': 'Módulo 550 Wp', 'categoria': 'modulo', 'fabricante': 'SolarTech',
			'modelo': 'ST550', 'potencia_nominal': '550',
		})
		equipamento = Equipamento.objects.get(nome='Módulo 550 Wp')
		self.client.post(reverse('novo_sistema'), {
			'projeto': projeto.pk, 'nome': 'Sistema principal', 'potencia_kwp': '5.5',
			'equipamento': equipamento.pk, 'quantidade': '10',
		})
		sistema = SistemaSolar.objects.get(nome='Sistema principal')
		self.assertEqual(sistema.equipamentos.count(), 1)

		arquivo = SimpleUploadedFile('memorial.pdf', b'conteudo tecnico', content_type='application/pdf')
		self.client.post(reverse('novo_documento'), {
			'projeto': projeto.pk, 'titulo': 'Memorial descritivo', 'tipo': 'memorial',
			'arquivo': arquivo,
		})
		self.assertEqual(DocumentoTecnico.objects.filter(projeto=projeto).count(), 1)

	def test_paginas_de_engenharia_renderizam(self):
		self.client.login(username='gestor', password='SenhaForte123!')

		for nome_url in ('engenharia', 'projetos', 'dimensionamentos', 'sistemas', 'equipamentos', 'documentos'):
			with self.subTest(nome_url=nome_url):
				resposta = self.client.get(reverse(nome_url))
				self.assertEqual(resposta.status_code, 200)

	def test_gestao_exporta_relatorio_e_registra_auditoria(self):
		self.client.login(username='gestor', password='SenhaForte123!')
		Cliente.objects.create(nome='Cliente Relatório', email='relatorio@solar.test')

		resposta = self.client.get(reverse('gestao'))
		self.assertEqual(resposta.status_code, 200)

		exportacao = self.client.get(reverse('exportar_relatorio') + '?tipo=clientes')
		self.assertEqual(exportacao.status_code, 200)
		self.assertIn('Cliente Relatório', exportacao.content.decode('utf-8-sig'))
		self.assertEqual(exportacao['Content-Type'], 'text/csv; charset=utf-8')

		self.client.post(reverse('configuracoes'), {
			'nome': 'Solar Gest Energia', 'cnpj': '00.000.000/0001-00', 'email': 'contato@solar.test',
			'telefone': '11999999999', 'moeda': 'BRL',
		})
		self.assertEqual(ConfiguracaoEmpresa.objects.get(pk=1).nome, 'Solar Gest Energia')
		self.assertTrue(Auditoria.objects.filter(usuario=self.usuario, rota=reverse('configuracoes')).exists())

	def test_paginas_de_gestao_renderizam(self):
		self.client.login(username='gestor', password='SenhaForte123!')

		for nome_url in ('gestao', 'relatorios', 'auditoria', 'configuracoes'):
			with self.subTest(nome_url=nome_url):
				resposta = self.client.get(reverse(nome_url))
				self.assertEqual(resposta.status_code, 200)
