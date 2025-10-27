import pytest
import re
from src.modelando_sistema_bancario_poo import (
    Cliente, PessoaFisica, Conta, ContaCorrente, Historico,
    Saque, Deposito, SistemaBancario, validar_cpf, verificar_contas,
    Transacao
)
from unittest.mock import patch, MagicMock, call
from src.constant import Constants
from io import StringIO
import sys


class TestConstants:
    """Testes para as constantes"""

    def test_constants_values(self):
        assert Constants.CPF_PATTERN == r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
        assert Constants.BRANCH == "0001"
        assert Constants.FAIL_CPF_MESSAGE == "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx."
        assert Constants.FAIL_VALUE_MESSAGE == "Operação falhou! O valor informado é inválido."
        assert Constants.FAIL_OPERATION_MESSAGE == "Operação falhou! Nenhuma conta cadastrada."
        assert Constants.INFO_CPF_MESSAGE == "Informe o CPF (formato xxx.xxx.xxx-xx): "
        assert Constants.INFO_ACCOUNT_NUMBER_MESSAGE == "Informe o número da conta: "
        assert Constants.FAIL_REGISTERED_CPF_MESSAGE == "Já existe um usuário com esse CPF!"


class TestDecorators:
    """Testes para os decoradores"""

    def test_validar_cpf_valido(self):
        @validar_cpf
        def dummy_function(cpf=None):
            return "success"

        result = dummy_function(cpf="123.456.789-00")
        assert result == "success"

    def test_validar_cpf_invalido(self, capsys):
        @validar_cpf
        def dummy_function(cpf=None):
            return "success"

        result = dummy_function(cpf="12345678900")
        captured = capsys.readouterr()
        assert result is None
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    def test_validar_cpf_sem_cpf(self):
        @validar_cpf
        def dummy_function():
            return "success"

        result = dummy_function()
        assert result == "success"

    def test_validar_cpf_com_args(self):
        @validar_cpf
        def dummy_function(cpf):
            return "success"

        result = dummy_function("123.456.789-00")
        assert result == "success"

    def test_verificar_contas_com_contas(self):
        class DummyClass:
            def __init__(self):
                self.contas = ["conta1"]

        @verificar_contas
        def dummy_method(self, *args, **kwargs):
            return "success"

        obj = DummyClass()
        result = dummy_method(obj)
        assert result == "success"

    def test_verificar_contas_sem_contas(self, capsys):
        class DummyClass:
            def __init__(self):
                self.contas = []

        @verificar_contas
        def dummy_method(self, *args, **kwargs):
            return "success"

        obj = DummyClass()
        result = dummy_method(obj)
        captured = capsys.readouterr()
        assert result is None
        assert Constants.FAIL_OPERATION_MESSAGE in captured.out


class TestCliente:
    """Testes para a classe Cliente"""

    def test_cliente_init(self):
        cliente = Cliente("Rua A, 123")
        assert cliente.endereco == "Rua A, 123"
        assert cliente.contas == []

    def test_cliente_adicionar_conta(self):
        cliente = Cliente("Rua A, 123")
        conta_mock = MagicMock()
        cliente.adicionar_conta(conta_mock)
        assert conta_mock in cliente.contas

    def test_cliente_realizar_transacao(self):
        cliente = Cliente("Rua A, 123")
        conta_mock = MagicMock()
        transacao_mock = MagicMock()

        cliente.realizar_transacao(conta_mock, transacao_mock)
        transacao_mock.registrar.assert_called_once_with(conta_mock)


class TestPessoaFisica:
    """Testes para a classe PessoaFisica"""

    def test_pessoa_fisica_init(self):
        pessoa = PessoaFisica(
            "João Silva",
            "01/01/1990",
            "123.456.789-00",
            "Rua A, 123"
        )
        assert pessoa.nome == "João Silva"
        assert pessoa.data_nascimento == "01/01/1990"
        assert pessoa.cpf == "123.456.789-00"
        assert pessoa.endereco == "Rua A, 123"
        assert pessoa.contas == []

    def test_pessoa_fisica_heranca(self):
        pessoa = PessoaFisica(
            "João Silva", "01/01/1990", "123.456.789-00", "Rua A, 123"
        )
        assert isinstance(pessoa, Cliente)


class TestConta:
    """Testes para a classe Conta"""

    def test_conta_init(self):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)

        assert conta._saldo == 0
        assert conta._numero == 1
        assert conta._agencia == Constants.BRANCH
        assert conta._cliente == cliente_mock
        assert isinstance(conta._historico, Historico)
        assert conta._extrato == ""

    def test_conta_properties(self):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)

        assert conta.saldo == 0
        assert conta.numero == 1
        assert conta.agencia == Constants.BRANCH
        assert conta.cliente == cliente_mock
        assert isinstance(conta.historico, Historico)
        assert conta.extrato == ""

    def test_conta_extrato_setter(self):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        conta.extrato = "Novo extrato"
        assert conta._extrato == "Novo extrato"

    def test_conta_depositar_valor_positivo(self):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.depositar(100.0)

        assert result is True
        assert conta.saldo == 100.0
        assert "Depósito: R$ 100.00" in conta.extrato

    def test_conta_depositar_valor_zero(self, capsys):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.depositar(0)

        captured = capsys.readouterr()
        assert result is False
        assert Constants.FAIL_VALUE_MESSAGE in captured.out

    def test_conta_depositar_valor_negativo(self, capsys):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.depositar(-50.0)

        captured = capsys.readouterr()
        assert result is False
        assert Constants.FAIL_VALUE_MESSAGE in captured.out

    def test_conta_sacar_valor_positivo_com_saldo(self):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        conta.depositar(200.0)
        result = conta.sacar(100.0)

        assert result is True
        assert conta.saldo == 100.0
        assert "Saque: R$ 100.00" in conta.extrato

    def test_conta_sacar_saldo_insuficiente(self, capsys):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.sacar(100.0)

        captured = capsys.readouterr()
        assert result is False
        assert "Operação falhou! Saldo insuficiente." in captured.out

    def test_conta_sacar_valor_zero(self, capsys):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.sacar(0)

        captured = capsys.readouterr()
        assert result is False
        assert Constants.FAIL_VALUE_MESSAGE in captured.out

    def test_conta_sacar_valor_negativo(self, capsys):
        cliente_mock = MagicMock()
        conta = Conta(1, cliente_mock)
        result = conta.sacar(-50.0)

        captured = capsys.readouterr()
        assert result is False
        assert Constants.FAIL_VALUE_MESSAGE in captured.out

    def test_conta_nova_conta(self):
        cliente_mock = MagicMock()
        conta = Conta.nova_conta(cliente_mock, 1)
        assert isinstance(conta, Conta)
        assert conta.numero == 1
        assert conta.cliente == cliente_mock


class TestContaCorrente:
    """Testes para a classe ContaCorrente"""

    def test_conta_corrente_init(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)

        assert conta._limite == 500
        assert conta._limite_saques == 3
        assert conta._numero_saques == 0

    def test_conta_corrente_init_com_parametros(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock, limite=1000, limite_saques=5)

        assert conta._limite == 1000
        assert conta._limite_saques == 5

    def test_conta_corrente_properties(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)

        assert conta.limite == 500
        assert conta.limite_saques == 3
        assert conta.numero_saques == 0

    def test_conta_corrente_numero_saques_setter(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        conta.numero_saques = 2
        assert conta._numero_saques == 2

    def test_conta_corrente_sacar_excede_limite(self, capsys):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        conta.depositar(1000.0)
        result = conta.sacar(600.0)

        captured = capsys.readouterr()
        assert result is False
        assert "Operação falhou! O valor do saque excede o limite." in captured.out

    def test_conta_corrente_sacar_excede_saques(self, capsys):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        conta.depositar(1000.0)

        # Realizar 3 saques
        for _ in range(3):
            conta.sacar(100.0)

        # Tentar quarto saque
        result = conta.sacar(100.0)

        captured = capsys.readouterr()
        assert result is False
        assert "Operação falhou! Número máximo de saques diários excedido." in captured.out

    def test_conta_corrente_sacar_sucesso(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        conta.depositar(1000.0)
        result = conta.sacar(100.0)

        assert result is True
        assert conta.saldo == 900.0
        assert conta.numero_saques == 1

    def test_conta_corrente_sacar_herdado_falha(self, capsys):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        result = conta.sacar(100.0)  # Sem saldo

        captured = capsys.readouterr()
        assert result is False
        assert "Operação falhou! Saldo insuficiente." in captured.out

    def test_conta_corrente_nova_conta(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente.nova_conta(cliente_mock, 1)
        assert isinstance(conta, ContaCorrente)
        assert conta.numero == 1
        assert conta.cliente == cliente_mock


class TestHistorico:
    """Testes para a classe Historico"""

    def test_historico_init(self):
        historico = Historico()
        assert historico._transacoes == []

    def test_historico_property(self):
        historico = Historico()
        assert historico.transacoes == []

    def test_historico_adicionar_transacao(self):
        historico = Historico()
        transacao_mock = MagicMock()
        transacao_mock.__class__.__name__ = "Saque"
        transacao_mock.valor = 100.0

        historico.adicionar_transacao(transacao_mock)

        assert len(historico.transacoes) == 1
        assert historico.transacoes[0]["tipo"] == "Saque"
        assert historico.transacoes[0]["valor"] == 100.0
        assert "data" in historico.transacoes[0]

    def test_historico_adicionar_multiplas_transacoes(self):
        historico = Historico()
        transacao1 = MagicMock()
        transacao1.__class__.__name__ = "Deposito"
        transacao1.valor = 200.0

        transacao2 = MagicMock()
        transacao2.__class__.__name__ = "Saque"
        transacao2.valor = 100.0

        historico.adicionar_transacao(transacao1)
        historico.adicionar_transacao(transacao2)

        assert len(historico.transacoes) == 2
        assert historico.transacoes[0]["tipo"] == "Deposito"
        assert historico.transacoes[1]["tipo"] == "Saque"


class TestTransacaoABC:
    """Testes para a classe abstrata Transacao"""

    def test_transacao_abc_nao_pode_ser_instanciada(self):
        with pytest.raises(TypeError):
            Transacao()

    def test_transacao_abc_tem_metodos_abstratos(self):
        assert hasattr(Transacao, 'valor')
        assert hasattr(Transacao, 'registrar')
        assert Transacao.registrar.__isabstractmethod__


class TestSaque:
    """Testes para a classe Saque"""

    def test_saque_init(self):
        saque = Saque(100.0)
        assert saque.valor == 100.0

    def test_saque_property(self):
        saque = Saque(150.0)
        assert saque.valor == 150.0

    def test_saque_registrar_sucesso(self):
        conta_mock = MagicMock()
        conta_mock.sacar.return_value = True
        conta_mock.historico = MagicMock()

        saque = Saque(100.0)
        saque.registrar(conta_mock)

        conta_mock.sacar.assert_called_once_with(100.0)
        conta_mock.historico.adicionar_transacao.assert_called_once_with(saque)

    def test_saque_registrar_falha(self):
        conta_mock = MagicMock()
        conta_mock.sacar.return_value = False
        conta_mock.historico = MagicMock()

        saque = Saque(100.0)
        saque.registrar(conta_mock)

        conta_mock.sacar.assert_called_once_with(100.0)
        conta_mock.historico.adicionar_transacao.assert_not_called()


class TestDeposito:
    """Testes para a classe Deposito"""

    def test_deposito_init(self):
        deposito = Deposito(200.0)
        assert deposito.valor == 200.0

    def test_deposito_property(self):
        deposito = Deposito(250.0)
        assert deposito.valor == 250.0

    def test_deposito_registrar_sucesso(self):
        conta_mock = MagicMock()
        conta_mock.depositar.return_value = True
        conta_mock.historico = MagicMock()

        deposito = Deposito(200.0)
        deposito.registrar(conta_mock)

        conta_mock.depositar.assert_called_once_with(200.0)
        conta_mock.historico.adicionar_transacao.assert_called_once_with(deposito)

    def test_deposito_registrar_falha(self):
        conta_mock = MagicMock()
        conta_mock.depositar.return_value = False
        conta_mock.historico = MagicMock()

        deposito = Deposito(200.0)
        deposito.registrar(conta_mock)

        conta_mock.depositar.assert_called_once_with(200.0)
        conta_mock.historico.adicionar_transacao.assert_not_called()


class TestSistemaBancario:
    """Testes para a classe SistemaBancario"""

    def test_sistema_bancario_init(self):
        sistema = SistemaBancario()
        assert sistema.clientes == []
        assert sistema.contas == []
        assert sistema.numero_conta == 1

    def test_filtrar_cliente_cpf_valido_encontrado(self):
        sistema = SistemaBancario()
        cliente = PessoaFisica(
            "João", "01/01/1990", "123.456.789-00", "Rua A"
        )
        sistema.clientes.append(cliente)

        resultado = sistema.filtrar_cliente(cpf="123.456.789-00")
        assert resultado == cliente

    def test_filtrar_cliente_cpf_valido_nao_encontrado(self):
        sistema = SistemaBancario()
        resultado = sistema.filtrar_cliente(cpf="123.456.789-00")
        assert resultado is None

    def test_filtrar_cliente_cpf_invalido(self, capsys):
        sistema = SistemaBancario()
        resultado = sistema.filtrar_cliente(cpf="12345678900")

        captured = capsys.readouterr()
        assert resultado is None
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    def test_filtrar_cliente_sem_cpf(self):
        sistema = SistemaBancario()
        resultado = sistema.filtrar_cliente("111.222.333-44")
        assert resultado is None

    def test_filtrar_conta_encontrada(self):
        sistema = SistemaBancario()
        cliente = PessoaFisica(
            "João", "01/01/1990", "123.456.789-00", "Rua A"
        )
        conta = ContaCorrente(1, cliente)
        sistema.contas.append(conta)

        resultado = sistema.filtrar_conta("123.456.789-00", "1")
        assert resultado == conta

    def test_filtrar_conta_nao_encontrada(self):
        sistema = SistemaBancario()
        resultado = sistema.filtrar_conta("123.456.789-00", "1")
        assert resultado is None

    def test_filtrar_conta_cpf_nao_corresponde(self):
        sistema = SistemaBancario()
        cliente = PessoaFisica(
            "João", "01/01/1990", "123.456.789-00", "Rua A"
        )
        conta = ContaCorrente(1, cliente)
        sistema.contas.append(conta)

        resultado = sistema.filtrar_conta("111.222.333-44", "1")
        assert resultado is None

    def test_filtrar_conta_numero_nao_corresponde(self):
        sistema = SistemaBancario()
        cliente = PessoaFisica(
            "João", "01/01/1990", "123.456.789-00", "Rua A"
        )
        conta = ContaCorrente(1, cliente)
        sistema.contas.append(conta)

        resultado = sistema.filtrar_conta("123.456.789-00", "2")
        assert resultado is None

    @patch('builtins.input')
    def test_menu(self, mock_input):
        mock_input.return_value = "d"
        sistema = SistemaBancario()
        resultado = sistema.menu()
        assert resultado == "d"

    @patch('builtins.input')
    def test_criar_usuario_sucesso(self, mock_input):
        mock_input.side_effect = [
            "123.456.789-00",  # CPF
            "João Silva",  # Nome
            "01/01/1990",  # Data nascimento
            "Rua A, 123"  # Endereço
        ]

        sistema = SistemaBancario()
        sistema.criar_usuario()

        assert len(sistema.clientes) == 1
        cliente = sistema.clientes[0]
        assert cliente.nome == "João Silva"
        assert cliente.cpf == "123.456.789-00"
        assert cliente.data_nascimento == "01/01/1990"
        assert cliente.endereco == "Rua A, 123"

    @patch('builtins.input')
    def test_criar_usuario_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"  # CPF inválido

        sistema = SistemaBancario()
        sistema.criar_usuario()

        captured = capsys.readouterr()
        assert len(sistema.clientes) == 0
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    @patch('builtins.input')
    def test_criar_usuario_cpf_ja_cadastrado(self, mock_input, capsys):
        mock_input.side_effect = [
            "123.456.789-00",  # CPF
            "João Silva",
            "01/01/1990",
            "Rua A, 123"
        ]

        sistema = SistemaBancario()
        sistema.criar_usuario()

        captured = capsys.readouterr()
        assert len(sistema.clientes) == 1

    @patch('builtins.input')
    def test_criar_usuario_data_invalida(self, mock_input, capsys):
        mock_input.side_effect = [
            "123.456.789-00",
            "João Silva",
            "01-01-1990",  # Data inválida
            "Rua A, 123"
        ]

        sistema = SistemaBancario()
        sistema.criar_usuario()

        captured = capsys.readouterr()
        assert len(sistema.clientes) == 0
        assert "Data de nascimento inválida" in captured.out

    @patch('builtins.input')
    def test_criar_conta_sucesso(self, mock_input):
        # Primeiro criar um cliente
        cliente = PessoaFisica(
            "João", "01/01/1990", "123.456.789-00", "Rua A"
        )

        mock_input.return_value = "123.456.789-00"

        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.criar_conta()

        assert len(sistema.contas) == 1
        assert sistema.numero_conta == 2
        conta = sistema.contas[0]
        assert conta.cliente == cliente
        assert conta.numero == 1
        assert cliente.contas[0] == conta

    @patch('builtins.input')
    def test_criar_conta_cliente_nao_encontrado(self, mock_input, capsys):
        mock_input.return_value = "123.456.789-00"

        sistema = SistemaBancario()
        sistema.criar_conta()

        captured = capsys.readouterr()
        assert len(sistema.contas) == 0
        assert "Usuário não encontrado" in captured.out

    @patch('builtins.input')
    def test_criar_conta_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"

        sistema = SistemaBancario()
        sistema.criar_conta()

        captured = capsys.readouterr()
        assert len(sistema.contas) == 0
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    @patch('builtins.input')
    def test_depositar_sucesso(self, mock_input):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.side_effect = [
            "123.456.789-00",  # CPF
            "1",  # Número da conta
            "100.0"  # Valor do depósito
        ]

        sistema.depositar()

        assert conta.saldo == 100.0

    @patch('builtins.input')
    def test_depositar_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"

        sistema = SistemaBancario()
        sistema.contas.append(MagicMock())  # Para passar pelo decorator
        sistema.depositar()

        captured = capsys.readouterr()
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    @patch('builtins.input')
    def test_depositar_valor_invalido(self, mock_input, capsys):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.side_effect = [
            "123.456.789-00",
            "1",
            "-50.0"  # Valor inválido
        ]

        sistema.depositar()

        captured = capsys.readouterr()
        assert "Operação falhou! O valor informado é inválido." in captured.out
        assert conta.saldo == 0.0

    @patch('builtins.input')
    def test_depositar_conta_nao_encontrada(self, mock_input, capsys):
        mock_input.side_effect = [
            "123.456.789-00",
            "999",  # Conta não existente
            "100.0"
        ]

        sistema = SistemaBancario()
        sistema.contas.append(MagicMock())  # Para passar pelo decorator
        sistema.depositar()

        captured = capsys.readouterr()
        assert Constants.FAIL_OPERATION_MESSAGE in captured.out

    @patch('builtins.input')
    def test_sacar_sucesso(self, mock_input):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        conta.depositar(500.0)  # Depositar primeiro
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.side_effect = [
            "123.456.789-00",
            "1",
            "100.0"
        ]

        sistema.sacar()

        assert conta.saldo == 400.0

    @patch('builtins.input')
    def test_sacar_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"

        sistema = SistemaBancario()
        sistema.contas.append(MagicMock())  # Para passar pelo decorator
        sistema.sacar()

        captured = capsys.readouterr()
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    @patch('builtins.input')
    def test_sacar_conta_nao_encontrada(self, mock_input, capsys):
        mock_input.side_effect = [
            "123.456.789-00",
            "999",
            "100.0"
        ]

        sistema = SistemaBancario()
        sistema.contas.append(MagicMock())  # Para passar pelo decorator
        sistema.sacar()

        captured = capsys.readouterr()
        assert Constants.FAIL_OPERATION_MESSAGE in captured.out

    @patch('builtins.input')
    def test_exibir_extrato_sucesso(self, mock_input, capsys):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        conta.depositar(300.0)
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.side_effect = [
            "123.456.789-00",
            "1"
        ]

        sistema.exibir_extrato()

        captured = capsys.readouterr()
        assert "=== Extrato ===" in captured.out
        assert "CPF: 123.456.789-00" in captured.out
        assert "Conta: 1" in captured.out
        assert "Depósito: R$ 300.00" in captured.out
        assert "Saldo atual: R$ 300.00" in captured.out

    @patch('builtins.input')
    def test_exibir_extrato_sem_movimentacoes(self, mock_input, capsys):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.side_effect = [
            "123.456.789-00",
            "1"
        ]

        sistema.exibir_extrato()

        captured = capsys.readouterr()
        assert "Não foram realizadas movimentações." in captured.out

    @patch('builtins.input')
    def test_exibir_extrato_conta_nao_encontrada(self, mock_input, capsys):
        mock_input.side_effect = [
            "123.456.789-00",
            "999"
        ]

        sistema = SistemaBancario()
        sistema.contas.append(MagicMock())  # Para passar pelo decorator
        sistema.exibir_extrato()

        captured = capsys.readouterr()
        assert Constants.FAIL_OPERATION_MESSAGE in captured.out

    @patch('builtins.input')
    def test_listar_contas_com_cpf(self, mock_input, capsys):
        cliente = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        conta = ContaCorrente(1, cliente)
        conta.depositar(500.0)
        sistema = SistemaBancario()
        sistema.clientes.append(cliente)
        sistema.contas.append(conta)

        mock_input.return_value = "123.456.789-00"

        sistema.listar_contas()

        captured = capsys.readouterr()
        assert "Agência: 0001" in captured.out
        assert "Número da Conta: 1" in captured.out
        assert "Titular: João" in captured.out
        assert "CPF: 123.456.789-00" in captured.out
        assert "Saldo: R$ 500.00" in captured.out

    @patch('builtins.input')
    def test_listar_contas_sem_cpf(self, mock_input, capsys):
        cliente1 = PessoaFisica("João", "01/01/1990", "123.456.789-00", "Rua A")
        cliente2 = PessoaFisica("Maria", "02/02/1985", "111.222.333-44", "Rua B")
        conta1 = ContaCorrente(1, cliente1)
        conta2 = ContaCorrente(2, cliente2)
        sistema = SistemaBancario()
        sistema.clientes.extend([cliente1, cliente2])
        sistema.contas.extend([conta1, conta2])

        mock_input.return_value = ""  # CPF vazio

        sistema.listar_contas()

        captured = capsys.readouterr()
        assert "João" in captured.out
        assert "Maria" in captured.out

    @patch('builtins.input')
    def test_listar_contas_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"

        sistema = SistemaBancario()
        sistema.listar_contas()

        captured = capsys.readouterr()
        assert Constants.FAIL_CPF_MESSAGE in captured.out

    @patch('builtins.input')
    def test_listar_contas_sem_contas(self, mock_input, capsys):
        mock_input.return_value = ""

        sistema = SistemaBancario()
        sistema.listar_contas()

        captured = capsys.readouterr()
        assert "Nenhuma conta encontrada." in captured.out

class TestIntegracao:
    """Testes de integração entre as classes"""

    def test_fluxo_completo_cliente_conta_transacao(self):
        # Criar cliente
        cliente = PessoaFisica(
            "Maria", "15/05/1985", "987.654.321-00", "Rua B, 456"
        )

        # Criar conta
        conta = ContaCorrente(1, cliente)
        cliente.adicionar_conta(conta)

        # Realizar transações
        deposito = Deposito(1000.0)
        saque = Saque(200.0)

        cliente.realizar_transacao(conta, deposito)
        cliente.realizar_transacao(conta, saque)

        # Verificar resultados
        assert conta.saldo == 800.0
        assert len(conta.historico.transacoes) == 2
        assert conta.numero_saques == 1

        # Verificar extrato
        assert "Depósito: R$ 1000.00" in conta.extrato
        assert "Saque: R$ 200.00" in conta.extrato

    def test_fluxo_multiplas_contas(self):
        # Criar cliente
        cliente = PessoaFisica(
            "Carlos", "10/10/1975", "111.222.333-44", "Rua C, 789"
        )

        # Criar múltiplas contas
        conta1 = ContaCorrente(1, cliente)
        conta2 = ContaCorrente(2, cliente)

        cliente.adicionar_conta(conta1)
        cliente.adicionar_conta(conta2)

        # Realizar transações em contas diferentes
        deposito1 = Deposito(500.0)
        deposito2 = Deposito(300.0)
        saque1 = Saque(100.0)

        cliente.realizar_transacao(conta1, deposito1)
        cliente.realizar_transacao(conta2, deposito2)
        cliente.realizar_transacao(conta1, saque1)

        # Verificar resultados
        assert conta1.saldo == 400.0
        assert conta2.saldo == 300.0
        assert len(cliente.contas) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.modelando_sistema_bancario_poo", "--cov-report=term-missing"])