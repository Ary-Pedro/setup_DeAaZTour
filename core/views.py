from django.shortcuts import render

def salvar_csvVenda(request, periodo, forma_pagamento=None):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
            "attachment; filename=Vendas_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    cabecalho = [
        "ID",
        "Cliente",
        "Vendedor",
        "Data da Venda",
        "Valor",
        "Situação",
        "Data Finalizado",
        "Tipo de Servico",
        "Forma de pagamento",
    ]

    # Variáveis para controle de inclusão das colunas de cidadania e nacionalidade
    incluir_cidadania = False
    incluir_nacionalidade = False

    if periodo == "hoje":
        vendas = Venda.objects.filter(data_venda=date.today())
    elif periodo == "semana":
        inicio_semana = date.today() - timedelta(days=date.today().weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        vendas = Venda.objects.filter(data_venda__gte=inicio_semana, data_venda__lte=fim_semana)
    elif periodo == "mes":
        inicio_mes = date.today().replace(day=1)
        proximo_mes = (inicio_mes + timedelta(days=31)).replace(day=1)
        vendas = Venda.objects.filter(data_venda__gte=inicio_mes, data_venda__lt=proximo_mes)
    else:
        vendas = Venda.objects.all()

    if forma_pagamento == "Pix":
        vendas = vendas.filter(tipo_pagamento="Pix")
    elif forma_pagamento == "Dinheiro":
        vendas = vendas.filter(tipo_pagamento="Dinheiro")
    elif forma_pagamento == "Credito":
        vendas = vendas.filter(tipo_pagamento="Credito")
    elif forma_pagamento == "Debito":
        vendas = vendas.filter(tipo_pagamento="Debito")


    # Verificar se algum tipo de cidadania ou nacionalidade foi preenchido
    for venda in vendas:
        if venda.tipo_cidadania and venda.tipo_cidadania != "S/D":
            incluir_cidadania = True
        if venda.nacionalidade and venda.nacionalidade != "S/D":
            incluir_nacionalidade = True

    # Adiciona as colunas de cidadania e nacionalidade ao cabeçalho, se necessário
    if incluir_cidadania:
        cabecalho.append("Tipo de Cidadania")
    if incluir_nacionalidade:
        cabecalho.append("Nacionalidade")

    writer.writerow(cabecalho)

    # Escrever os dados das vendas
    for venda in vendas:
        if venda.tipo_servico == "Outros":
            tipo_servico = venda.tipo_servico_outros
        else:
            tipo_servico = venda.tipo_servico

        if venda.tipo_cidadania == "Outros":
            tipo_cidadania = venda.tipo_cidadania_outros if venda.tipo_cidadania_outros else "S/D"
        else:
            tipo_cidadania = venda.tipo_cidadania if venda.tipo_cidadania else "S/D"

        if venda.nacionalidade == "Outros":
            nacionalidade = venda.nacionalidade_outros if venda.nacionalidade_outros else "S/D"
        else:
            nacionalidade = venda.nacionalidade if venda.nacionalidade else "S/D"

        linha = [
            venda.id,
            venda.cliente.nome,
            (
                f"{venda.vendedor.first_name} {venda.vendedor.last_name}"
                if venda.vendedor
                else "S/D"
            ),
            venda.data_venda.strftime('%d/%m/%Y'),
            venda.valor,
            venda.situacaoMensal,
            venda.finished_at.strftime('%d/%m/%Y') if venda.finished_at else "S/D",
            tipo_servico,
            venda.tipo_pagamento,
        ]

        # Adiciona os valores de cidadania e nacionalidade, se forem incluídos no cabeçalho
        if incluir_cidadania:
            linha.append(tipo_cidadania)
        if incluir_nacionalidade:
            linha.append(nacionalidade)

        writer.writerow(linha)

    return response


def salvar_csvClientes(request, periodo):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
            "attachment; filename=dadosClientes_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "Nome",
            "Celular",
            "Sexo",
            "Data de Nascimento",
            "Endereço",
            "Bairro",
            "Estado",
            "CEP",
            "RG",
            "CPF",
            "Número de Passaporte",
            "Idade",
            "Anexo 1",
            "Anexo 2",
            "Anexo 3",
        ]
    )  # Cabeçalho do CSV

    if periodo == "hoje":
        clientes = CadCliente.objects.filter(created_at__date=date.today())
    elif periodo == "semana":
        inicio_semana = date.today() - timedelta(days=date.today().weekday())
        clientes = CadCliente.objects.filter(created_at__date__gte=inicio_semana)
    elif periodo == "mes":
        inicio_mes = date.today().replace(day=1)
        clientes = CadCliente.objects.filter(created_at__date__gte=inicio_mes)
    else:
        clientes = CadCliente.objects.all()

    for cliente in clientes:
        anexo1_url = request.build_absolute_uri(cliente.anexo1.url) if cliente.anexo1 else "S/D"
        anexo2_url = request.build_absolute_uri(cliente.anexo2.url) if cliente.anexo2 else "S/D"
        anexo3_url = request.build_absolute_uri(cliente.anexo3.url) if cliente.anexo3 else "S/D"

        writer.writerow(
            [
                cliente.nome,
                cliente.celular,
                cliente.get_sexo_display(),  # Obtém o texto legível para a escolha do sexo
                cliente.data_nascimento.strftime('%d/%m/%Y'),
                cliente.endereco,
                cliente.bairro,
                cliente.estado,
                cliente.cep,
                cliente.rg,
                cliente.cpf,
                cliente.num_passaporte,
                cliente.idade() if cliente.idade() else "S/D",
                f'=HYPERLINK("{anexo1_url}", "{os.path.basename(cliente.anexo1.name)}")' if anexo1_url != "S/D" else "S/D",
                f'=HYPERLINK("{anexo2_url}", "{os.path.basename(cliente.anexo2.name)}")' if anexo2_url != "S/D" else "S/D",
                f'=HYPERLINK("{anexo3_url}", "{os.path.basename(cliente.anexo3.name)}")' if anexo3_url != "S/D" else "S/D",
            ]
        )
    return response
