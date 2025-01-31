document.addEventListener('DOMContentLoaded', function() {
    const idClienteInput = document.querySelector('input[name="pk_cliente"]');
    const cpfClienteInput = document.querySelector('input[name="cpf_cliente"]');
    const dataNascimentoClienteInput = document.querySelector('input[name="data_nascimento_cliente"]');
    const cepClienteInput = document.querySelector('input[name="cep_cliente"]');

    idClienteInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        e.target.value = value;
    });

    cpfClienteInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 11) value = value.slice(0, 11);
        formattedValue = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');

        e.target.value = formattedValue;
    });

    dataNascimentoClienteInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 8) value = value.slice(0, 8);
        formattedValue = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');

        e.target.value = formattedValue;
    });

    cepClienteInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 8) value = value.slice(0, 8);
        formattedValue = value.replace(/(\d{5})(\d{3})/, '$1-$2');

        e.target.value = formattedValue;
    });
});