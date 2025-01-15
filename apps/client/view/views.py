from django.shortcuts import render


class cadCliente(LoginRequiredMixin, CreateView):
    login_url = "log"  # URL para redirecionar para login

    model = CadCliente
    fields = [
        "nome",
        "celular",
        "cpf",
        "rg",
        "sexo",
        "data_nascimento",
        "num_passaporte",
        "endereco",
        "bairro",
        "estado",
        "cep",
        'anexo1',
        'anexo2',
        'anexo3',
    ]
    template_name = "cadAdmin/Cliente/formsCliente/cadastroCliente_form.html"
    success_url = reverse_lazy("homeAdmin")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"Cliente de id {self.object.id} cadastrado com sucesso!"
        )
        return response


class CadListView(LoginRequiredMixin, ListView):
    model = CadCliente
    paginate_by = 20
    template_name = "cadAdmin/Cliente/formsCliente/cadastroCliente_list.html"
    context_object_name = "cadastro_list"
    login_url = "log"  # URL para redirecionar para login