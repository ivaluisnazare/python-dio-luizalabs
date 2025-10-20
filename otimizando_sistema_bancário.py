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

def depositar(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print("Depósito realizado com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")
    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    if valor > saldo:
        print("Operação falhou! Saldo insuficiente.")
    elif valor > limite:
        print("Operação falhou! O valor do saque excede o limite.")
    elif numero_saques >= limite_saques:
        print("Operação falhou! Número máximo de saques diários excedido.")
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        print("Saque realizado com sucesso!")
    else:
        print("Operação falhou! O valor informado é inválido.")
    return saldo, extrato, numero_saques

def exibir_extrato(saldo, /, *, extrato):
    print("\n=== Extrato ===")
    if extrato == "":
        print("Não foram realizadas movimentações.")
    else:
        print(extrato)
    print(f"Saldo: R$ {saldo:.2f}")
    print("================")

def criar_usuario(usuarios):
    import re
    from datetime import datetime
    cpf = input("Informe o CPF (formato xxx.xxx.xxx-xx): ").strip()
    if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
        print("CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx com 11 dígitos.")
        return
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("Já existe um usuário com esse CPF!")
        return
    nome = input("Informe o nome completo: ").strip()
    data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ").strip()
    try:
        datetime.strptime(data_nascimento, "%d/%m/%Y")
    except ValueError:
        print("Data de nascimento inválida! Utilize o formato DD/MM/AAAA.")
        return
    endereco = input("Informe o endereço (logradouro, número - bairro - cidade/sigla estado): ").strip()
    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})
    print("Usuário criado com sucesso!")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(agencia, numero_conta, usuarios):
    cpf = input("Informe o CPF do usuário (formato xxx.xxx.xxx-xx): ")
    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        conta = {"agencia": agencia, "numero_conta": numero_conta, "usuario": usuario}
        print("Conta criada com sucesso!")
        return conta
    print("Usuário não encontrado, fluxo de criação de conta encerrado.")
    return None

def listar_contas(contas):
    cpf = input("Informe o CPF, (formato xxx.xxx.xxx-xx), para filtrar as contas (pressione Enter para listar todas): ").strip()
    print()
    contas_filtradas = contas
    if cpf:
        contas_filtradas = [conta for conta in contas if conta["usuario"].get("cpf") == cpf]
        if not contas_filtradas:
            print("Nenhuma conta encontrada para o CPF informado.")
            return
    for conta in contas_filtradas:
        usuario = conta["usuario"]
        print("==============================")
        print(f"""\
Agência: {conta['agencia']}
Número da Conta: {conta['numero_conta']}
Titular: {usuario['nome']}
CPF: {usuario.get('cpf', 'N/A')}""")

def main():
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    limite_saques = 3
    usuarios = []
    contas = []
    agencia = "0001"
    numero_conta = 1
    while True:
        opcao = menu()
        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = depositar(saldo, valor, extrato)
        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))
            saldo, extrato, numero_saques = sacar(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=limite_saques,
            )
        elif opcao == "e":
            exibir_extrato(saldo, extrato=extrato)
        elif opcao == "n":
            conta = criar_conta(agencia, numero_conta, usuarios)
            if conta:
                contas.append(conta)
                numero_conta += 1
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "nu":
            criar_usuario(usuarios)
        elif opcao == "q":
            break
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

if __name__ == "__main__":
    main()

