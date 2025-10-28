import re
from abc import ABC, abstractmethod
from datetime import datetime

from src.constant import Constants


def validar_cpf(func):
    def wrapper(*args, **kwargs):
        cpf = kwargs.get("cpf") or (args[1] if len(args) > 1 else None)
        if cpf and not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return None
        return func(*args, **kwargs)

    return wrapper


def verificar_contas(func):
    def wrapper(self, *args, **kwargs):
        if not self.contas:
            print(Constants.FAIL_OPERATION_MESSAGE)
            return None
        return func(self, *args, **kwargs)

    return wrapper


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = Constants.BRANCH
        self._cliente = cliente
        self._historico = Historico()
        self._extrato = ""

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @property
    def extrato(self):
        return self._extrato

    @extrato.setter
    def extrato(self, value):
        self._extrato = value

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação falhou! Saldo insuficiente.")
            return False
        elif valor > 0:
            self._saldo -= valor
            self._extrato += f"Saque: R$ {valor:.2f}\n"
            return True
        else:
            print(Constants.FAIL_VALUE_MESSAGE)
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            self._extrato += f"Depósito: R$ {valor:.2f}\n"
            return True
        else:
            print(Constants.FAIL_VALUE_MESSAGE)
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
        self._numero_saques = 0

    @property
    def numero_saques(self):
        return self._numero_saques

    @numero_saques.setter
    def numero_saques(self, value):
        self._numero_saques = value

    @property
    def limite(self):
        return self._limite

    @property
    def limite_saques(self):
        return self._limite_saques

    def sacar(self, valor):
        excedeu_limite = valor > self._limite
        excedeu_saques = self._numero_saques >= self._limite_saques

        if excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite.")
            return False
        elif excedeu_saques:
            print("Operação falhou! Número máximo de saques diários excedido.")
            return False
        else:
            sucesso = super().sacar(valor)
            if sucesso:
                self._numero_saques += 1
            return sucesso


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class SistemaBancario:
    def __init__(self):
        self.clientes = []
        self.contas = []
        self.numero_conta = 1

    def menu(self):
        print("\n=== Menu ===")
        print("[d] Depositar")
        print("[s] Sacar")
        print("[e] Extrato")
        print("[q] Sair")
        print("[n] Nova Conta")
        print("[lc] Listar Contas")
        print("[nu] Novo Usuário")
        return input("Escolha uma opção: ").lower()

    @validar_cpf
    def filtrar_cliente(self, cpf):
        clientes_filtrados = [
            cliente for cliente in self.clientes if cliente.cpf == cpf
        ]
        return clientes_filtrados[0] if clientes_filtrados else None

    def filtrar_conta(self, cpf, numero_conta):
        for conta in self.contas:
            if str(conta.numero) == numero_conta and conta.cliente.cpf == cpf:
                return conta
        return None

    @verificar_contas
    def depositar(self, cpf=None, numero_conta=None):
        if cpf is None:
            cpf = input(Constants.INFO_CPF_MESSAGE).strip()

        if not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return

        if numero_conta is None:
            numero_conta = input(Constants.INFO_ACCOUNT_NUMBER_MESSAGE).strip()

        valor = float(input("Informe o valor do depósito: "))
        if valor <= 0:
            print("Operação falhou! O valor informado é inválido.")
            return

        conta = self.filtrar_conta(cpf, numero_conta)
        if not conta:
            print(Constants.FAIL_OPERATION_MESSAGE)
            return

        transacao = Deposito(valor)
        conta.cliente.realizar_transacao(conta, transacao)
        print("Depósito realizado com sucesso!")

    @verificar_contas
    def sacar(self):
        cpf = input(Constants.INFO_CPF_MESSAGE).strip()
        if not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return

        numero_conta = input(Constants.INFO_ACCOUNT_NUMBER_MESSAGE).strip()
        valor = float(input("Informe o valor do saque: "))

        conta = self.filtrar_conta(cpf, numero_conta)
        if not conta:
            print(Constants.FAIL_OPERATION_MESSAGE)
            return

        transacao = Saque(valor)
        conta.cliente.realizar_transacao(conta, transacao)

    @verificar_contas
    def exibir_extrato(self):
        cpf = input(Constants.INFO_CPF_MESSAGE).strip()
        numero_conta = input(Constants.INFO_ACCOUNT_NUMBER_MESSAGE).strip()

        conta = self.filtrar_conta(cpf, numero_conta)
        if not conta:
            print(Constants.FAIL_OPERATION_MESSAGE)
            return

        print("\n=== Extrato ===")
        print(f"CPF: {cpf} | Conta: {numero_conta}")

        if not conta.extrato.strip():
            print("Não foram realizadas movimentações.")
        else:
            print(conta.extrato.strip())

        print(f"Saldo atual: R$ {conta.saldo:.2f}")
        print("================")

    def criar_usuario(self):
        cpf = input(Constants.INFO_CPF_MESSAGE).strip()
        if not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return

        cliente = self.filtrar_cliente(cpf)
        if cliente:
            print(Constants.FAIL_REGISTERED_CPF_MESSAGE)
            return

        nome = input("Informe o nome completo: ").strip()
        data_nascimento = input("Informe a data de nascimento (DD/MM/AAAA): ").strip()

        try:
            datetime.strptime(data_nascimento, "%d/%m/%Y")
        except ValueError:
            print("Data de nascimento inválida! Utilize o formato DD/MM/AAAA.")
            return

        endereco = input(
            "Informe o endereço (logradouro, número - bairro - cidade/sigla estado): "
        ).strip()

        cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
        self.clientes.append(cliente)
        print("Usuário criado com sucesso!")

    def criar_conta(self):
        cpf = input(Constants.INFO_CPF_MESSAGE).strip()

        if not re.match(Constants.CPF_PATTERN, cpf):
            print(Constants.FAIL_CPF_MESSAGE)
            return

        cliente = self.filtrar_cliente(cpf)
        if not cliente:
            print("Usuário não encontrado, fluxo de criação de conta encerrado.")
            return

        conta = ContaCorrente.nova_conta(cliente=cliente, numero=self.numero_conta)
        self.contas.append(conta)
        cliente.adicionar_conta(conta)
        self.numero_conta += 1
        print("Conta criada com sucesso!")

    def listar_contas(self):
        cpf = input(Constants.INFO_CPF_MESSAGE).strip()

        contas_filtradas = self.contas
        if cpf:
            if not re.match(Constants.CPF_PATTERN, cpf):
                print(Constants.FAIL_CPF_MESSAGE)
                return
            contas_filtradas = [
                conta for conta in self.contas if conta.cliente.cpf == cpf
            ]

        if not contas_filtradas:
            print("Nenhuma conta encontrada.")
            return

        print()
        for conta in contas_filtradas:
            usuario = conta.cliente
            saldo = conta.saldo
            print("==============================")
            print(
                f"""\
Agência: {conta.agencia}
Número da Conta: {conta.numero}
Titular: {usuario.nome}
CPF: {usuario.cpf}
Saldo: R$ {saldo:.2f}"""
            )

    def executar(self):
        while True:
            opcao = self.menu()

            if opcao == "d":
                self.depositar()
            elif opcao == "s":
                self.sacar()
            elif opcao == "e":
                self.exibir_extrato()
            elif opcao == "n":
                self.criar_conta()
            elif opcao == "lc":
                self.listar_contas()
            elif opcao == "nu":
                self.criar_usuario()
            elif opcao == "q":
                break
            else:
                print(
                    "Operação inválida, por favor selecione novamente a operação desejada."
                )


def main():
    sistema = SistemaBancario()
    sistema.executar()


if __name__ == "__main__":
    main()
