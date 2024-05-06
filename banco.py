from abc import ABC, abstractclassmethod, abstractproperty, abstractmethod
from datetime import datetime
import textwrap

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
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
    
    def sacar(self, valor):
        saldo = self.saldo
        if valor < 0:
            print("Quantia inválida")
        elif valor > saldo:
            print("Saldo insuficiente")
        else: 
            self._saldo -= valor
            print("Saque realizado com sucesso!")
            return True
        return False
    def depositar(self, valor):
        if valor < 0:
            print("Quantia inválida")
        else:
            self._saldo += valor
            print("Depósito realizado com sucesso!")
            return True
        return False
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__])

        if valor > self.limite:
            print("Limite ultrapassado")
        elif numero_saques >= self.limite_saques:
            print("Limite de saque excedido")
        else:
            return super().sacar(valor)
        return False
    
    def __str__(self):
        return f"""\
            Agência:\{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            """
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
                # "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass
    @classmethod
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

def menu():
    menu = """\n
    ========== MENU ==========
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [c]\tNova Conta
    [l]\tListar Contas
    [u]\tNovo Usuário
    [q]\tSair
    =>
"""
    return input(textwrap.dedent(menu))

def saque(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Usuário não encontrado!")
        return
    valor = float(input("Informe o valor do saque:"))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)


def deposito(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Usuário não encontrado!")
        return
    
    valor = float(input("Informe o valor do depósito:"))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui conta!")
        return
    # Não permite cliente escolher conta
    return cliente.contas[0]

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("Usuário não encontrado!")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    print("\n========== EXTRATO ==========")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"
    
    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("====================")

        
def criar_cliente(clientes):
    cpf = input("informe o cpf:")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("Usuário já existente!")
        return
    nome = input("Informe o nome do usuário:")
    data_nascimento = input("Informe a data de nascimento:")
    endereco = input("Informe o endereço:")

    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(cliente)

    print("Usuário criado com sucesso!")
    
    
def criar_conta_corrente(numero_da_conta, clientes, contas):
    cpf = input("informe o cpf do cliente:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Usuário não encontrado!")
        return
    
    conta = ContaCorrente.nova_conta(cliente, numero_da_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso!")

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    
    return clientes_filtrados[0] if clientes_filtrados else None

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []
    while True:
        opcao = menu()

        if opcao == 'd':
            deposito(clientes)   
        elif opcao == 's':
            saque(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "u":
            criar_cliente(clientes)
        elif opcao == "c":
            numero_da_conta = len(contas) + 1
            criar_conta_corrente(numero_da_conta, clientes, contas)
        elif opcao == "l":
            listar_contas(contas)
        elif opcao == "q":
            break;

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")   

main() 