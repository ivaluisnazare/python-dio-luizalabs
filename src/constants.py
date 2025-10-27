class Constants:
    CPF_PATTERN = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"

    FAIL_CPF_MESSAGE = "CPF inválido! O CPF deve estar no formato xxx.xxx.xxx-xx."
    FAIL_OPERATION_MESSAGE = "Operação falhou! Nenhuma conta cadastrada."
    FAIL_INVALID_ACCOUNT_MESSAGE = "Operação falhou! Conta não encontrada para o CPF informado."
    FAIL_REGISTERED_CPF_MESSAGE = "Já existe um usuário com esse CPF!"
    FAIL_REGISTERED_ACCOUNT_MESSAGE = "Usuário não encontrado, fluxo de criação de conta encerrado."
    FAIL_VALUE_MESSAGE = "Operação falhou! O valor informado é inválido."

    INFO_CPF_MESSAGE = "Informe o CPF (formato xxx.xxx.xxx-xx): "
    INFO_ACCOUNT_NUMBER_MESSAGE = "Informe o número da conta: "

    BRANCH = "0001"
    WITHDRAWAL_LIMIT = 1000.00
    DAILY_WITHDRAWAL_LIMIT = 3