document.addEventListener('DOMContentLoaded', function () {
    function formatarData(input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            e.target.value = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');
        });
    }

    function formatarCPF(input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            e.target.value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        });
    }

    function formatarCEP(input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            e.target.value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
        });
    }

    function formatarNumericoComVirgula(input) {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/[^0-9.,]/g, '');

            // Garante apenas uma vírgula ou ponto
            const parts = value.split(/[,\.]/);
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }

            e.target.value = value;
        });

        // Converte vírgula em ponto ao sair do campo (blur)
        input.addEventListener('blur', function (e) {
            e.target.value = e.target.value.replace(',', '.');
        });
    }

    function formatarNumero(input) {
        input.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    // Campos comuns
    const idClienteInput = document.querySelector('input[name="pk_cliente"]');
    const cpfClienteInput = document.querySelector('input[name="cpf_cliente"]');
    const dataNascimentoClienteInput = document.querySelector('input[name="data_nascimento_cliente"]');
    const cepClienteInput = document.querySelector('input[name="cep_cliente"]');
    const comecovendaClienteInput = document.getElementById('id_data_venda');
    const fimvendaClienteInput = document.getElementById('id_finished_at');

    // Campos de valores
   // Captura dos inputs
   const valorVendaInput        = document.getElementById('id_valor');
   const custoPadraoInput       = document.getElementById('id_custo_padrao_venda');
   const descontoInput          = document.getElementById('id_desconto');
   const custoSobreVendaInput   = document.getElementById('id_custo_sobre_venda');

    if (idClienteInput) formatarNumero(idClienteInput);
    if (cpfClienteInput) formatarCPF(cpfClienteInput);
    if (cepClienteInput) formatarCEP(cepClienteInput);

    if (dataNascimentoClienteInput) formatarData(dataNascimentoClienteInput);
    if (comecovendaClienteInput) formatarData(comecovendaClienteInput);
    if (fimvendaClienteInput) formatarData(fimvendaClienteInput);

    if (valorVendaInput)      formatarNumericoComVirgula(valorVendaInput);
    if (custoPadraoInput)     formatarNumericoComVirgula(custoPadraoInput);
    if (descontoInput)        formatarNumericoComVirgula(descontoInput);
    if (custoSobreVendaInput) formatarNumericoComVirgula(custoSobreVendaInput);
    [valorVendaInput, custoPadraoInput, descontoInput, custoSobreVendaInput]
    .forEach(input => {
      if (input && input.value.trim() !== '') {
        input.dispatchEvent(new Event('input'));
        input.dispatchEvent(new Event('blur'));
      }
    });
});