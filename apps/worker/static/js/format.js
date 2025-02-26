document.addEventListener('DOMContentLoaded', function() {
    const telefoneInput = document.querySelector('input[name="telefone"]');
    const cpfInput = document.querySelector('input[name="cpf"]');
    const dataNascimentoInput = document.querySelector('input[name="data_nascimento"]');

    telefoneInput.addEventListener('input', function(e) {
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
    });

    cpfInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 11) value = value.slice(0, 11);
        formattedValue = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');

        e.target.value = formattedValue;
    });

    dataNascimentoInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        let formattedValue = '';

        if (value.length > 8) value = value.slice(0, 8);
        formattedValue = value.replace(/(\d{2})(\d{2})(\d{4})/, '$1/$2/$3');

        e.target.value = formattedValue;
    });
});