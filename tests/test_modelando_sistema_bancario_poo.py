import pytest
from src.modelando_sistema_bancario_poo import (Cliente, PessoaFisica,
                                                Conta, ContaCorrente,
                                                Historico, Saque,
                                                Deposito, SistemaBancario,
                                                validar_cpf, verificar_contas)
from unittest.mock import patch, MagicMock
from src.constant import Constants

class TestConstants:
    """Testes para as constantes"""

    def test_constants_values(self):
        assert Constants.CPF_PATTERN == r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
        assert Constants.BRANCH == "0001"


class TestDecorators:

    def test_validar_cpf_valido(self):
        @validar_cpf
        def dummy_function(cpf=None):
            return "success"

        result = dummy_function("123.456.789-00")
        assert result == "success"

    def test_validar_cpf_invalido(self, capsys):
        @validar_cpf
        def dummy_function(cpf=None):
            return "success"

        result = dummy_function("12345678900")
        captured = capsys.readouterr()
        assert result is "success"
        assert '' in captured.out

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


class TestContaCorrente:
    """Testes para a classe ContaCorrente"""

    def test_conta_corrente_init(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)

        assert conta._limite == 500
        assert conta._limite_saques == 3
        assert conta._numero_saques == 0

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
        assert "O valor do saque excede o limite." in captured.out

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
        assert "Número máximo de saques diários excedido." in captured.out

    def test_conta_corrente_sacar_sucesso(self):
        cliente_mock = MagicMock()
        conta = ContaCorrente(1, cliente_mock)
        conta.depositar(1000.0)
        result = conta.sacar(100.0)

        assert result is True
        assert conta.saldo == 900.0
        assert conta.numero_saques == 1


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


class TestTransacoes:
    """Testes para as classes de transação"""

    def test_saque_init(self):
        saque = Saque(100.0)
        assert saque.valor == 100.0

    def test_deposito_init(self):
        deposito = Deposito(200.0)
        assert deposito.valor == 200.0

    def test_saque_registrar_sucesso(self):
        conta_mock = MagicMock()
        conta_mock.sacar.return_value = True
        conta_mock.historico = MagicMock()

        saque = Saque(100.0)
        saque.registrar(conta_mock)

        conta_mock.sacar.assert_called_once_with(100.0)
        conta_mock.historico.adicionar_transacao.assert_called_once_with(saque)

    def test_deposito_registrar_sucesso(self):
        conta_mock = MagicMock()
        conta_mock.depositar.return_value = True
        conta_mock.historico = MagicMock()

        deposito = Deposito(200.0)
        deposito.registrar(conta_mock)

        conta_mock.depositar.assert_called_once_with(200.0)
        conta_mock.historico.adicionar_transacao.assert_called_once_with(deposito)


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

    @patch('builtins.input')
    def test_criar_usuario_cpf_invalido(self, mock_input, capsys):
        mock_input.return_value = "12345678900"  # CPF inválido

        sistema = SistemaBancario()
        sistema.criar_usuario()

        captured = capsys.readouterr()
        assert len(sistema.clientes) == 0
        assert Constants.FAIL_CPF_MESSAGE in captured.out

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

    @patch('builtins.input')
    def test_criar_conta_cliente_nao_encontrado(self, mock_input, capsys):
        mock_input.return_value = "123.456.789-00"

        sistema = SistemaBancario()
        sistema.criar_conta()

        captured = capsys.readouterr()
        assert len(sistema.contas) == 0
        assert "Usuário não encontrado" in captured.out


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


# Testes auxiliares para cobertura
def test_conta_nova_conta():
    cliente_mock = MagicMock()
    conta = Conta.nova_conta(cliente_mock, 1)
    assert isinstance(conta, Conta)
    assert conta.numero == 1
    assert conta.cliente == cliente_mock


def test_cliente_realizar_transacao():
    cliente = Cliente("Rua A")
    conta_mock = MagicMock()
    transacao_mock = MagicMock()

    cliente.realizar_transacao(conta_mock, transacao_mock)
    transacao_mock.registrar.assert_called_once_with(conta_mock)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])