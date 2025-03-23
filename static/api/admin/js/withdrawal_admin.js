(function($) {
    $(document).ready(function() {
        function showHideFields() {
            var accountType = $('#id_account_type').val();

            // Hide all fields related to bank account and crypto address
            $('.field-bank_name, .field-owner_name, .field-bank_account, .field-crypto_address, .field-network').hide();

            // Show fields based on the selected account type
            if (accountType === 'crypto') {
                $('.field-crypto_address, .field-network').show();
            } else {
                $('.field-bank_name, .field-owner_name, .field-bank_account').show();
            }
        }

        // Initial call to show/hide fields based on the default account type
        showHideFields();

        // Bind the function to the change event of the account type field
        $('#id_account_type').change(function() {
            showHideFields();
        });
    });
})(django.jQuery);
