import pytest
from src.otimizando_sistema_bancario import (criar_conta, criar_usuario,
                                             depositar, encontrar_conta,
                                             exibir_extrato, filtrar_usuario,
                                             listar_contas, menu, sacar)


@pytest.fixture
def contas_fixture():
    return [
        {
            "numero_conta": "12345",
            "agencia": "0001",
            "usuario": {
                "cpf": "111.222.333-44",
                "nome": "João",
                "endereco": "Rua A, 123",
            },
            "saldo": 500.0,
            "extrato": "",
            "numero_saques": 0,
            "limite": 500,
            "limite_saques": 3,
        },
        {
            "numero_conta": "67890",
            "agencia": "0001",
            "usuario": {
                "cpf": "555.666.777-88",
                "nome": "Maria",
                "endereco": "Rua B, 456",
            },
            "saldo": 1000.0,
            "extrato": "",
            "numero_saques": 0,
            "limite": 500,
            "limite_saques": 3,
        },
    ]


@pytest.fixture
def usuarios_fixture():
    return [
        {
            "nome": "João Silva",
            "data_nascimento": "01/01/1990",
            "cpf": "111.222.333-44",
            "endereco": "Rua A, 123 - Centro - São Paulo/SP",
        },
        {
            "nome": "Maria Santos",
            "data_nascimento": "15/05/1985",
            "cpf": "555.666.777-88",
            "endereco": "Rua B, 456 - Jardim - Rio de Janeiro/RJ",
        },
    ]


def test_depositar_valido(contas_fixture, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "200")
    contas_atualizadas = depositar(
        contas_fixture, cpf="111.222.333-44", numero_conta="12345"
    )
    conta = encontrar_conta(contas_atualizadas, "111.222.333-44", "12345")
    assert conta["saldo"] == 700.0
    assert "Depósito: R$ 200.00" in conta["extrato"]


def test_depositar_sem_contas(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "200")
    contas_atualizadas = depositar([], cpf="111.222.333-44", numero_conta="12345")
    captured = capsys.readouterr()
    assert "Operação falhou! Nenhuma conta cadastrada." in captured.out
    assert contas_atualizadas == []


def test_depositar_cpf_invalido(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "200")
    contas_atualizadas = depositar(
        contas_fixture, cpf="11122233344", numero_conta="12345"
    )
    captured = capsys.readouterr()
    assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out
    assert contas_atualizadas == contas_fixture


def test_depositar_valor_negativo(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "-50")
    contas_atualizadas = depositar(
        contas_fixture, cpf="111.222.333-44", numero_conta="12345"
    )
    captured = capsys.readouterr()
    assert "Operação falhou! O valor informado é inválido." in captured.out
    assert contas_atualizadas == contas_fixture


def test_depositar_valor_invalido_string(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "abc")
    contas_atualizadas = depositar(
        contas_fixture, cpf="111.222.333-44", numero_conta="12345"
    )
    captured = capsys.readouterr()
    assert "Operação falhou! Valor inválido." in captured.out
    assert contas_atualizadas == contas_fixture


def test_depositar_conta_nao_encontrada(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "100")
    contas_atualizadas = depositar(
        contas_fixture, cpf="999.888.777-66", numero_conta="00000"
    )
    captured = capsys.readouterr()
    assert (
        "Operação falhou! Conta não encontrada para o CPF informado.\n" in captured.out
    )
    assert contas_atualizadas == contas_fixture


def test_sacar_valido(contas_fixture, monkeypatch, capsys):
    inputs = ["555.666.777-88", "67890", "300"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    contas_atualizadas = sacar(contas_fixture)
    conta = encontrar_conta(contas_atualizadas, "555.666.777-88", "67890")

    captured = capsys.readouterr()
    assert "Saque realizado com sucesso!" in captured.out
    assert conta["saldo"] == 700.0
    assert "Saque: R$ 300.00" in conta["extrato"]
    assert conta["numero_saques"] == 1


def test_sacar_sem_contas(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "100")
    contas_atualizadas = sacar([])
    captured = capsys.readouterr()
    assert "Operação falhou! Nenhuma conta cadastrada." in captured.out
    assert contas_atualizadas == []


def test_sacar_cpf_invalido(contas_fixture, monkeypatch, capsys):
    inputs = ["55566677788", "67890", "300"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out
    assert contas_atualizadas == contas_fixture


def test_sacar_valor_negativo(contas_fixture, monkeypatch, capsys):
    inputs = ["555.666.777-88", "67890", "-100"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "Operação falhou! O valor informado é inválido." in captured.out
    assert contas_atualizadas == contas_fixture


def test_sacar_valor_invalido_string(contas_fixture, monkeypatch, capsys):
    inputs = ["555.666.777-88", "67890", "abc"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "Operação falhou! Valor inválido." in captured.out
    assert contas_atualizadas == contas_fixture


def test_sacar_saldo_insuficiente(contas_fixture, monkeypatch, capsys):
    inputs = ["111.222.333-44", "12345", "600"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "Operação falhou! Saldo insuficiente." in captured.out
    assert contas_atualizadas == contas_fixture


def test_sacar_limite_excedido(contas_fixture, monkeypatch, capsys):
    inputs = ["111.222.333-44", "12345", "600"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    conta = encontrar_conta(contas_fixture, "111.222.333-44", "12345")
    conta["limite"] = 400

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "Operação falhou! Saldo insuficiente.\n" in captured.out
    assert contas_atualizadas == contas_fixture


def test_sacar_limite_saques_excedido(contas_fixture, monkeypatch, capsys):
    inputs = ["111.222.333-44", "12345", "100"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    conta = encontrar_conta(contas_fixture, "111.222.333-44", "12345")
    conta["numero_saques"] = 3

    contas_atualizadas = sacar(contas_fixture)
    captured = capsys.readouterr()
    assert "Operação falhou! Número máximo de saques diários excedido." in captured.out
    assert contas_atualizadas == contas_fixture


def test_exibir_extrato_valido(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "200")
    depositar(contas_fixture, cpf="111.222.333-44", numero_conta="12345")

    inputs = ["111.222.333-44", "12345"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    exibir_extrato(contas_fixture)
    captured = capsys.readouterr()
    assert "=== Extrato ===" in captured.out
    assert "Depósito: R$ 200.00" in captured.out
    assert "Saldo atual: R$ 700.00" in captured.out


def test_exibir_extrato_sem_movimentacoes(contas_fixture, monkeypatch, capsys):
    inputs = ["555.666.777-88", "67890"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    exibir_extrato(contas_fixture)
    captured = capsys.readouterr()
    assert "Não foram realizadas movimentações." in captured.out
    assert "Saldo atual: R$ 1000.00" in captured.out


def test_exibir_extrato_sem_contas(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "123")
    exibir_extrato([])
    captured = capsys.readouterr()
    assert "Operação falhou! Nenhuma conta cadastrada." in captured.out


def test_exibir_extrato_conta_nao_encontrada(contas_fixture, monkeypatch, capsys):
    inputs = ["999.888.777-66", "00000"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    exibir_extrato(contas_fixture)
    captured = capsys.readouterr()
    assert (
        "Operação falhou! Conta não encontrada para o CPF informado.\n" in captured.out
    )


def test_encontrar_conta_existente(contas_fixture):
    conta = encontrar_conta(contas_fixture, "111.222.333-44", "12345")
    assert conta is not None
    assert conta["usuario"]["nome"] == "João"


def test_encontrar_conta_inexistente(contas_fixture):
    conta = encontrar_conta(contas_fixture, "999.888.777-66", "00000")
    assert conta is None


def test_encontrar_conta_somente_cpf(contas_fixture):
    conta = encontrar_conta(contas_fixture, "555.666.777-88", None)
    assert conta is None


def test_encontrar_conta_somente_numero(contas_fixture):
    conta = encontrar_conta(contas_fixture, None, numero_conta="12345")
    assert conta is None


def test_encontrar_conta_nenhum_parametro(contas_fixture):
    conta = encontrar_conta(contas_fixture, None, None)
    assert conta is None


def test_criar_usuario_valido(usuarios_fixture, monkeypatch, capsys):
    inputs = [
        "123.456.789-00",
        "Carlos Silva",
        "20/10/1980",
        "Rua C, 789 - Centro - Belo Horizonte/MG",
    ]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    novos_usuarios = criar_usuario(usuarios_fixture.copy())
    captured = capsys.readouterr()
    assert "Usuário criado com sucesso!" in captured.out
    assert len(novos_usuarios) == len(usuarios_fixture) + 1


def test_criar_usuario_cpf_existente(usuarios_fixture, monkeypatch, capsys):
    inputs = ["111.222.333-44", "João Silva", "01/01/1990", "Rua A, 123"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    novos_usuarios = criar_usuario(usuarios_fixture.copy())
    captured = capsys.readouterr()
    assert "Já existe um usuário com esse CPF!" in captured.out
    assert len(novos_usuarios) == len(usuarios_fixture)


def test_criar_usuario_cpf_invalido(usuarios_fixture, monkeypatch, capsys):
    inputs = ["12345678900", "Carlos Silva", "20/10/1980", "Rua C, 789"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    novos_usuarios = criar_usuario(usuarios_fixture.copy())
    captured = capsys.readouterr()
    assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out
    assert len(novos_usuarios) == len(usuarios_fixture)


def test_criar_usuario_data_invalida(usuarios_fixture, monkeypatch, capsys):
    inputs = ["123.456.789-00", "Carlos Silva", "20-10-1980", "Rua C, 789"]
    input_iter = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

    novos_usuarios = criar_usuario(usuarios_fixture.copy())
    captured = capsys.readouterr()
    assert "Data de nascimento inválida! Utilize o formato DD/MM/AAAA." in captured.out
    assert len(novos_usuarios) == len(usuarios_fixture)


def test_filtrar_usuario_existente(usuarios_fixture):
    usuario = filtrar_usuario("111.222.333-44", usuarios_fixture)
    assert usuario is not None
    assert usuario["nome"] == "João Silva"


def test_filtrar_usuario_inexistente(usuarios_fixture):
    usuario = filtrar_usuario("999.888.777-66", usuarios_fixture)
    assert usuario is None


def test_criar_conta_valida(usuarios_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "111.222.333-44")
    conta = criar_conta("0001", "10001", usuarios_fixture)

    captured = capsys.readouterr()
    assert "Conta criada com sucesso!" in captured.out
    assert conta is not None
    assert conta["agencia"] == "0001"
    assert conta["numero_conta"] == "10001"
    assert conta["usuario"]["cpf"] == "111.222.333-44"
    assert conta["saldo"] == 0


def test_criar_conta_cpf_invalido(usuarios_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "11122233344")
    conta = criar_conta("0001", "10001", usuarios_fixture)

    captured = capsys.readouterr()
    assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out
    assert conta is None


def test_criar_conta_usuario_nao_encontrado(usuarios_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "999.888.777-66")
    conta = criar_conta("0001", "10001", usuarios_fixture)

    captured = capsys.readouterr()
    assert (
        "Usuário não encontrado, fluxo de criação de conta encerrado." in captured.out
    )
    assert conta is None


def test_listar_contas_todas(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "")
    listar_contas(contas_fixture)

    captured = capsys.readouterr()
    assert "João" in captured.out
    assert "Maria" in captured.out
    assert "Agência: 0001" in captured.out


def test_listar_contas_por_cpf(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "111.222.333-44")
    listar_contas(contas_fixture)

    captured = capsys.readouterr()
    assert "João" in captured.out
    assert "Maria" not in captured.out


def test_listar_contas_cpf_invalido(contas_fixture, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "11122233344")
    listar_contas(contas_fixture)

    captured = capsys.readouterr()
    assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out


def test_listar_contas_vazias(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "")
    listar_contas([])

    captured = capsys.readouterr()
    assert "Nenhuma conta encontrada." in captured.out


def test_menu(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "d")
    opcao = menu()
    assert opcao == "d"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=src.otimizando_sistema_bancario",
            "--cov-report=term-missing",
        ]
    )
