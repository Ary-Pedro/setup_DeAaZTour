document.addEventListener('DOMContentLoaded', function() {
    function formatarData(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // Remove não numéricos
            if (value.length > 8) value = value.slice(0, 8);
            e.target.value = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');
        });
    }

    function formatarCPF(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) value = value.slice(0, 11);
            e.target.value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
        });
    }

    function formatarCEP(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.slice(0, 8);
            e.target.value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
        });
    }

    function formatarNumero(input) {
        input.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    // Captura de elementos com verificação para evitar erro se o campo não existir
    const idClienteInput = document.querySelector('input[name="pk_cliente"]');
    const cpfClienteInput = document.querySelector('input[name="cpf_cliente"]');
    const dataNascimentoClienteInput = document.querySelector('input[name="data_nascimento_cliente"]');
    const cepClienteInput = document.querySelector('input[name="cep_cliente"]');
    const comecovendaClienteInput = document.getElementById('id_data_venda');
    const fimvendaClienteInput = document.getElementById('id_finished_at');

    if (idClienteInput) formatarNumero(idClienteInput);
    if (cpfClienteInput) formatarCPF(cpfClienteInput);
    if (cepClienteInput) formatarCEP(cepClienteInput);
    if (dataNascimentoClienteInput) formatarData(dataNascimentoClienteInput);
    if (comecovendaClienteInput) formatarData(comecovendaClienteInput);
    if (fimvendaClienteInput) formatarData(fimvendaClienteInput);
});
