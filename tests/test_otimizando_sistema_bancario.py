import pytest
from src.otimizando_sistema_bancario import depositar, sacar, encontrar_conta
from src.constant import Constants
@pytest.fixture
def contas_fixture():
    return [
        {
            "numero_conta": "12345",
            "usuario": {"cpf": "111.222.333-44", "nome": "João"},
            "saldo": 500.0,
            "extrato": ""
        },
        {
            "numero_conta": "67890",
            "usuario": {"cpf": "555.666.777-88", "nome": "Maria"},
            "saldo": 1000.0,
            "extrato": ""
        }
    ]

def test_depositar_valido(contas_fixture, monkeypatch):
        monkeypatch.setattr(Constants, "CPF_PATTERN", r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', raising=False)
        monkeypatch.setattr('builtins.input', lambda _: "200")
        monkeypatch.setattr(Constants, "CPF_PATTERN", r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
        contas_atualizadas = depositar(contas_fixture, cpf="111.222.333-44", numero_conta="12345")
        conta = encontrar_conta(contas_atualizadas, "111.222.333-44", "12345")
        assert conta["saldo"] == 700.0
        assert "Depósito: R$ 200.00" in conta["extrato"]


def test_depositar_cpf_invalido(contas_fixture, monkeypatch, capsys):
        inputs = iter(["11122233344", "200"])
        monkeypatch.setattr('builtins.input', lambda _: "200")
        monkeypatch.setattr(Constants, "CPF_PATTERN", r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
        contas_atualizadas = depositar(contas_fixture, cpf="11122233344", numero_conta="12345")
        captured = capsys.readouterr()
        assert "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx." in captured.out
        conta = encontrar_conta(contas_atualizadas, "11122233344", "12345")
        assert conta is None

def test_depositar_valor_invalido(contas_fixture, monkeypatch):
    inputs = iter(["111.222.333-44", "-50"])
    monkeypatch.setattr('builtins.input', lambda _: "-50")
    contas_atualizadas = depositar(contas_fixture, cpf="111.222.333-44", numero_conta="12345")
    conta = encontrar_conta(contas_atualizadas, "111.222.333-44", "12345")
    assert  "" in conta["extrato"]

def test_sacar_valido(contas_fixture, monkeypatch):
    inputs = iter(["555.666.777-88", "300"])
    monkeypatch.setattr('builtins.input', lambda _: "300")
    contas_atualizadas = sacar(contas_fixture)
    conta = encontrar_conta(contas_atualizadas, "555.666.777-88", "67890")
    assert '' in ''

def test_sacar_cpf_invalido(contas_fixture, monkeypatch):
    inputs = iter(["55566677788", "300"])
    monkeypatch.setattr('builtins.input', lambda _: "300")
    contas_atualizadas = sacar(contas_fixture)
    conta = encontrar_conta(contas_atualizadas, "55566677788", "67890")
    assert conta is None

def test_sacar_valor_invalido(contas_fixture, monkeypatch):
    inputs = iter(["555.666.777-88", "-100"])
    monkeypatch.setattr('builtins.input', lambda _: "-100")
    contas_atualizadas = sacar(contas_fixture)
    conta = encontrar_conta(contas_atualizadas, "555.666.777-88", "67890")
    assert "" in conta["extrato"]

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

if __name__ == "__main__":
    pytest.main()
