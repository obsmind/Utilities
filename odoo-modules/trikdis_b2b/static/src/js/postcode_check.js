/**
 * Trikdis UK — postcode territory blocker
 *
 * 1. Shows an error banner if the URL contains ?postcode_blocked=1
 *    (set by the server when a blocked postcode was submitted).
 * 2. Validates the postcode field in real-time and prevents form
 *    submission if a blocked prefix is detected.
 *
 * Blocked prefixes:
 *   BT  — Northern Ireland
 *   GY  — Guernsey
 *   JE  — Jersey
 *   IM  — Isle of Man
 */

(function () {
    'use strict';

    var BLOCKED_RE = /^(BT|GY|JE|IM)\d/i;

    var ERROR_MSG = (
        'Sorry, we currently only deliver within Great Britain ' +
        '(England, Scotland and Wales). ' +
        'We do not accept orders for Northern Ireland (BT), ' +
        'the Channel Islands (GY / JE), or the Isle of Man (IM). ' +
        'Please contact us at ' +
        '<a href="mailto:hello@uk.trikdis.com">hello@uk.trikdis.com</a> ' +
        'if you have a query.'
    );

    function buildBanner(msg) {
        var div = document.createElement('div');
        div.className = 'alert alert-danger mt-3 mb-3';
        div.setAttribute('role', 'alert');
        div.id = 'trikdis-postcode-error';
        div.innerHTML = '<strong>Delivery not available.</strong> ' + msg;
        return div;
    }

    function showBanner(container) {
        if (document.getElementById('trikdis-postcode-error')) return;
        var banner = buildBanner(ERROR_MSG);
        container.insertBefore(banner, container.firstChild);
        banner.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function removeBanner() {
        var existing = document.getElementById('trikdis-postcode-error');
        if (existing) existing.remove();
    }

    function getZipField() {
        return (
            document.querySelector('input[name="zip"]') ||
            document.querySelector('input[id="zip"]') ||
            document.querySelector('input[name="zipcode"]')
        );
    }

    function getFormContainer(zipField) {
        var form = zipField.closest('form');
        return form || zipField.parentElement;
    }

    document.addEventListener('DOMContentLoaded', function () {

        // 1. Show banner if server redirected here with postcode_blocked=1
        var params = new URLSearchParams(window.location.search);
        if (params.get('postcode_blocked') === '1') {
            var zipField = getZipField();
            if (zipField) {
                showBanner(getFormContainer(zipField));
                zipField.focus();
            }
        }

        // 2. Real-time validation
        var zipField = getZipField();
        if (!zipField) return;

        function validate() {
            var val = zipField.value.trim();
            if (BLOCKED_RE.test(val)) {
                showBanner(getFormContainer(zipField));
                zipField.style.borderColor = '#dc3545';
            } else {
                removeBanner();
                zipField.style.borderColor = '';
            }
        }

        zipField.addEventListener('input', validate);
        zipField.addEventListener('blur', validate);

        // 3. Block form submission
        var form = zipField.closest('form');
        if (form) {
            form.addEventListener('submit', function (e) {
                var val = zipField.value.trim();
                if (BLOCKED_RE.test(val)) {
                    e.preventDefault();
                    showBanner(getFormContainer(zipField));
                    zipField.focus();
                }
            });
        }
    });
})();
