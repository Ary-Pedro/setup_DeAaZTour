from datetime import date

from homeAdmin.models import CadCliente, CustomUser_Funcionario, Venda


class CadastroEspelho(CadCliente):
    class Meta:
        proxy = True


class CustomUser_FuncionarioEspelho(CustomUser_Funcionario):
    class Meta:
        proxy = True


class VendaEspelho(Venda):
    class Meta:
        proxy = True

    def mark_has_complete (self):
        if not self.finished_at:
            self.finished_at = date.today()
            self.situacao = 'Finalizada'
            self.save()
