(function($, fjord, remoteTroubleshooting, document, window) {
    'use strict';

    $(document).ready(function() {
        /**
         * Switches to the card with id #cardId. This also updates the
         * window history via pushState.
         */
        function changeCard(cardId, firstCard) {
            // Make active card inactive
            $('.card:not(.inactive)').addClass('inactive');

            // Set title, add back-button, make new card active
            var $card = $('#' + cardId);
            $('header h1').text($card.attr('data-title'));
            if ($card.attr('data-back-id') !== undefined) {
                $('#back-button-container').show();
            } else {
                $('#back-button-container').hide();
            }
            $card.removeClass('inactive');
            if ($card.attr('data-focus') !== undefined) {
                $($card.attr('data-focus')).focus();
            }
            if (!firstCard) {
                window.history.pushState({page: cardId}, '', '#' + cardId);
            }
        }

        window.onpopstate = function(ev) {
            // Switches the the appropriate card
            var pageId = ev.state ? ev.state.page : 'intro';
            changeCard(pageId);
        };

        /**
         * Makes the submit button valid/invalid depending on whether
         * the form is valid.
         */
        function toggleSubmitButton() {
            var isValid = true;

            if ($('#description').val().replace(/^\s+/, '') === '' ||
                    $('#description').hasClass('invalid') ||
                    $('#id_url').hasClass('invalid') ||
                    $('#id_email').hasClass('invalid')) {
                isValid = false;
            }

            $('#form-submit-btn').prop('disabled', !isValid);
        }

        fjord.countRemaining($('#description'));

        $('#description').on('input', function() {
            fjord.countRemaining(this);
            if ($(this).val().replace(/^\s+/, '') === '') {
                $(this).addClass('invalid');
            } else {
                $(this).removeClass('invalid');
            }
            toggleSubmitButton();
        });

        $('#id_url').on('input', function() {
            var url = $.trim($(this).val());
            if (fjord.validateUrl(url) || !url.length) {
                $(this).removeClass('invalid');
            } else {
                $(this).addClass('invalid');
            }
            toggleSubmitButton();
        });

        $('#id_email').on('input', function() {
            if (fjord.validateEmail($(this).val())) {
                $(this).removeClass('invalid');
            } else {
                $(this).addClass('invalid');
            }
            toggleSubmitButton();
        });

        $('#happy-button').click(function(ev) {
            $('.happy').show();
            $('.sad').hide();
            $('#id_happy').val(1);
            changeCard('moreinfo');
            return false;
        });
        $('#happy-button').keypress(function(ev) {
            if ((ev.keyCode || ev.which) === '13') {
                $('#happy-button').click();
            }
        });
        $('#sad-button').click(function(ev) {
            $('.happy').hide();
            $('.sad').show();
            $('#id_happy').val(0);
            changeCard('moreinfo');
            return false;
        });
        $('#sad-button').keypress(function(ev) {
            if ((ev.keyCode || ev.which) === '13') {
                $('#sad-button').click();
            }
        });
        $('#back-button-container').click(function(ev) {
            // We do what the browser back button would do here. We
            // use #back-button-container because svg elements can't
            // do tabindex in Firefox (bug #778654).
            window.history.back();
            return false;
        });
        $('#back-button-container').keypress(function(ev) {
            if ((ev.keyCode || ev.which) === '13') {
                $('#back-button-container').click();
            }
        });
        $('#email-ok').on('change', function() {
            var checked = $(this).is(':checked');
            $('#id_email').prop('disabled', !checked);
        });

        // If there's a hash and a word, wipe it out with a
        // replaceState.
        if (window.location.hash.match(/^#\w+$/)) {
            window.history.replaceState('', '', '#');
        }

        var browserData;

        // Hide the "browser-ask" section by default. Only show it if
        // the api is there and there's data.
        $('#browser-ask').hide();

        remoteTroubleshooting.available(function (yesno) {
            if (yesno) {
                $('#browser-ask').show();
                remoteTroubleshooting.getData(function (data) {
                    browserData = data;
                    if ($('#browser-ok').is(':checked')) {
                        $('#browser-data').val(JSON.stringify(browserData));
                    }
                });
            }
        });

        $('#browser-ok').on('change', function() {
            var checked = $(this).is(':checked');
            if (checked && browserData) {
                $('#browser-data').val(JSON.stringify(browserData));
            } else {
                $('#browser-data').val('{}');
            }
        });

        changeCard('intro', true);
    });
}(jQuery, fjord, remoteTroubleshooting, document, window));
