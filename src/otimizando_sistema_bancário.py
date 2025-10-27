from constants import Constants
import re
from datetime import datetime


def menu():
    print("\n=== Menu ===")
    print("[d] Depositar")
    print("[s] Sacar")
    print("[e] Extrato")
    print("[q] Sair")
    print("[n] Nova Conta")
    print("[lc] Listar Contas")
    print("[nu] Novo Usuário")
    return input("Escolha uma opção: ").lower()


def encontrar_conta(contas, cpf, numero_conta):
    """Função auxiliar para encontrar uma conta específica"""
    for conta in contas:
        if (str(conta.get("numero_conta")) == numero_conta and
                conta.get("usuario", {}).get("cpf") == cpf):
            return conta
    return None


def depositar(contas, cpf=None, numero_conta=None):
    if not contas:
        print("Operação falhou! Nenhuma conta cadastrada.")
        return contas

    if cpf is None:
        cpf = input("Informe o CPF (formato xxx.xxx.xxx-xx): ").strip()
    if not re.match(Constants.CPF_PATTERN, cpf):
        print("CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx.")
        return contas

    if numero_conta is None:
        numero_conta = input("Informe o número da conta: ").strip()

    try:
        valor = float(input("Informe o valor do depósito: "))
        if valor <= 0:
            print("Operação falhou! O valor informado é inválido.")
            return contas
    except ValueError:
        print("Operação falhou! Valor inválido.")
        return contas

    conta_encontrada = encontrar_conta(contas, cpf, numero_conta)
    if not conta_encontrada:
        print(Constants.FAIL_INVALID_ACCOUNT_MESSAGE)
        return contas

    saldo_atual = conta_encontrada.get("saldo", 0)
    conta_encontrada["saldo"] = saldo_atual + valor

    extrato_conta = conta_encontrada.get("extrato", "")
    extrato_conta += f"Depósito: R$ {valor:.2f}\n"
    conta_encontrada["extrato"] = extrato_conta

    print("Depósito realizado com sucesso!")
    return contas


def sacar(contas):
    if not contas:
        print(Constants.FAIL_OPERATION_MESSAGE)
        return contas

    cpf = input(Constants.INFO_CPF_MESSAGE).strip()
    if not re.match(Constants.CPF_PATTERN, cpf):
        print(Constants.FAIL_CPF_MESSAGE)
        return contas

    numero_conta = input(Constants.INFO_ACCOUNT_NUMBER_MESSAGE).strip()

    try:
        valor = float(input("Informe o valor do saque: "))
    except ValueError:
        print("Operação falhou! Valor inválido.")
        return contas

    conta_encontrada = encontrar_conta(contas, cpf, numero_conta)
    if not conta_encontrada:
        print(Constants.FAIL_INVALID_ACCOUNT_MESSAGE)
        return contas

    saldo_conta = conta_encontrada.get("saldo", 0)
    limite = conta_encontrada.get("limite", 500)
    numero_saques = conta_encontrada.get("numero_saques", 0)
    limite_saques = conta_encontrada.get("limite_saques", 3)

    excedeu_saldo = valor > saldo_conta
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("Operação falhou! Saldo insuficiente.")
        return contas
    elif excedeu_limite:
        print("Operação falhou! O valor do saque excede o limite.")
        return contas
    elif excedeu_saques:
        print("Operação falhou! Número máximo de saques diários excedido.")
        return contas
    elif valor <= 0:
        print("Operação falhou! O valor informado é inválido.")
        return contas

    # Realizar saque
    conta_encontrada["saldo"] = saldo_conta - valor
    conta_encontrada["numero_saques"] = numero_saques + 1

    extrato_conta = conta_encontrada.get("extrato", "")
    extrato_conta += f"Saque: R$ {valor:.2f}\n"
    conta_encontrada["extrato"] = extrato_conta

    print("Saque realizado com sucesso!")
    return contas


def exibir_extrato(contas):
    if not contas:
        print(Constants.FAIL_OPERATION_MESSAGE)
        return

    cpf = input("Informe o CPF (formato xxx.xxx.xxx-xx): ").strip()
    numero_conta = input(Constants.INFO_ACCOUNT_NUMBER_MESSAGE).strip()

    conta_encontrada = encontrar_conta(contas, cpf, numero_conta)
    if not conta_encontrada:
        print(Constants.FAIL_INVALID_ACCOUNT_MESSAGE)
        return

    saldo_conta = conta_encontrada.get("saldo", 0)
    extrato_conta = conta_encontrada.get("extrato", "")

    print("\n=== Extrato ===")
    print(f"CPF: {cpf} | Conta: {numero_conta}")

    if not extrato_conta.strip():
        print("Não foram realizadas movimentações.")
    else:
        print(extrato_conta.strip())

    print(f"Saldo atual: R$ {saldo_conta:.2f}")
    print("================")


def criar_usuario(usuarios):
    cpf = input(Constants.INFO_CPF_MESSAGE).strip()
    if not re.match(Constants.CPF_PATTERN, cpf):
        print(Constants.FAIL_CPF_MESSAGE)
        return usuarios

    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("Já existe um usuário com esse CPF!")
        return usuarios

    nome = input("Informe o nome completo: ").strip()
    data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ").strip()

    try:
        datetime.strptime(data_nascimento, "%d/%m/%Y")
    except ValueError:
        print("Data de nascimento inválida! Utilize o formato DD/MM/AAAA.")
        return usuarios

    endereco = input(
        "Informe o endereço (logradouro, número - bairro - cidade/sigla estado): "
    ).strip()

    usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco,
    })

    print("Usuário criado com sucesso!")
    return usuarios


def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None


def criar_conta(agencia, numero_conta, usuarios):
    cpf = input(Constants.INFO_CPF_MESSAGE).strip()

    if not re.match(Constants.CPF_PATTERN, cpf):
        print(Constants.FAIL_CPF_MESSAGE)
        return None

    usuario = filtrar_usuario(cpf, usuarios)
    if not usuario:
        print("Usuário não encontrado, fluxo de criação de conta encerrado.")
        return None

    conta = {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "usuario": usuario,
        "saldo": 0,
        "extrato": "",
        "numero_saques": 0,
        "limite": 500,
        "limite_saques": 3,
    }

    print("Conta criada com sucesso!")
    return conta


def listar_contas(contas):
    cpf = input(Constants.INFO_CPF_MESSAGE).strip()

    contas_filtradas = contas
    if cpf:
        if not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return
        contas_filtradas = [
            conta for conta in contas if conta["usuario"].get("cpf") == cpf
        ]

    if not contas_filtradas:
        print("Nenhuma conta encontrada.")
        return

    print()
    for conta in contas_filtradas:
        usuario = conta["usuario"]
        saldo = conta.get("saldo", 0)
        print("==============================")
        print(f"""\
Agência: {conta['agencia']}
Número da Conta: {conta['numero_conta']}
Titular: {usuario['nome']}
CPF: {usuario.get('cpf', 'N/A')}
Saldo: R$ {saldo:.2f}""")


def main():
    usuarios = []
    contas = []
    agencia = "0001"
    numero_conta = 1

    while True:
        opcao = menu()

        if opcao == "d":
            contas = depositar(contas)
        elif opcao == "s":
            contas = sacar(contas)
        elif opcao == "e":
            exibir_extrato(contas)
        elif opcao == "n":
            conta = criar_conta(agencia, numero_conta, usuarios)
            if conta:
                contas.append(conta)
                numero_conta += 1
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "nu":
            usuarios = criar_usuario(usuarios)
        elif opcao == "q":
            break
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")


if __name__ == "__main__":
    main()