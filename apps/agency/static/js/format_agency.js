document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');

    const telefoneInputs = [
        document.getElementById('id_telefone1'),
        document.getElementById('id_telefone2'),
        document.getElementById('id_telefone3')
    ];
    const cnpjInput = document.getElementById('id_cnpj');
    const cepInput = document.getElementById('id_cep');
    const contatoAnoInput = document.getElementById('id_contato_ano');

    console.log('Telefone Inputs:', telefoneInputs);
    console.log('CNPJ Input:', cnpjInput);
    console.log('CEP Input:', cepInput);
    console.log('Contato Ano Input:', contatoAnoInput);

    telefoneInputs.forEach(function(telefoneInput, index) {
        if (telefoneInput) {
            telefoneInput.addEventListener('input', function(e) {
                console.log(`Telefone${index + 1} Input Event:`, e.target.value);
                let value = e.target.value.replace(/\D/g, '');
                let formattedValue = '';

                if (e.target.value.startsWith('+') && !e.target.value.startsWith('+55')) {
                    e.target.value = e.target.value;
                    return;
                }

                if (value.startsWith('55')) {
                    value = '+' + value;
                }

                if (value.startsWith('+55')) {
                    if (value.length > 14) value = value.slice(0, 14);
                    formattedValue = value.replace(/(\+\d{2})(\d{2})(\d{4,5})(\d{4})/, '$1 ($2) $3-$4');
                } else if (value.startsWith('55')) {
                    if (value.length > 13) value = value.slice(0, 13);
                    formattedValue = value.replace(/(\d{2})(\d{2})(\d{4,5})(\d{4})/, '+$1 ($2) $3-$4');
                } else if (value.startsWith('0')) {
                    if (value.length > 11) value = value.slice(0, 11);
                    formattedValue = value.replace(/(\d{2})(\d{4,5})(\d{4})/, '($1) $2-$3');
                } else if (value.length > 10) {
                    if (value.length > 11) value = value.slice(0, 11);
                    formattedValue = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                } else {
                    if (value.length > 10) value = value.slice(0, 10);
                    formattedValue = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                }

                e.target.value = formattedValue;
                console.log(`Formatted Telefone${index + 1} Value:`, formattedValue);
            });
        } else {
            console.log(`Telefone${index + 1} input not found`);
        }
    });

    if (cnpjInput) {
        cnpjInput.addEventListener('input', function(e) {
            console.log('CNPJ Input Event:', e.target.value);
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length > 14) value = value.slice(0, 14);
            formattedValue = value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');

            e.target.value = formattedValue;
            console.log('Formatted CNPJ Value:', formattedValue);
        });
    } else {
        console.log('CNPJ input not found');
    }

    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            console.log('CEP Input Event:', e.target.value);
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length > 8) value = value.slice(0, 8);
            formattedValue = value.replace(/(\d{5})(\d{3})/, '$1-$2');

            e.target.value = formattedValue;
            console.log('Formatted CEP Value:', formattedValue);
        });
    } else {
        console.log('CEP input not found');
    }

    if (contatoAnoInput) {
        contatoAnoInput.addEventListener('input', function(e) {
            console.log('Contato Ano Input Event:', e.target.value);
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length > 8) value = value.slice(0, 8);
            formattedValue = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');

            e.target.value = formattedValue;
            console.log('Formatted Contato Ano Value:', formattedValue);
        });
    } else {
        console.log('Contato Ano input not found');
    }
});