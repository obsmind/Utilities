/**
 * Trikdis UK — Cookie Consent + Google Consent Mode v2
 * Uses vanilla-cookieconsent v3 (MIT)
 *
 * GA4 Measurement ID: G-YFT1MZLHRK
 *
 * Flow:
 *   1. GCM v2 defaults set to 'denied' immediately (before any gtag calls)
 *   2. Cookie banner shown on first visit
 *   3. On Accept Analytics → GA4 loaded dynamically + GCM updated
 *   4. On Accept Marketing → GCM ad signals updated (Google Ads / Meta ready)
 */

(function () {
    'use strict';

    var GA4_ID = 'G-YFT1MZLHRK';

    // ── 1. Google Consent Mode v2 defaults (must fire before gtag.js) ──────
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;  // expose globally so GA4 snippet can reuse it

    gtag('consent', 'default', {
        analytics_storage:  'denied',
        ad_storage:         'denied',
        ad_user_data:       'denied',
        ad_personalization: 'denied',
        wait_for_update:    500
    });
    gtag('js', new Date());

    // ── 2. Helpers ──────────────────────────────────────────────────────────
    function loadGA4() {
        if (document.querySelector('script[src*="googletagmanager.com/gtag"]')) {
            // gtag.js already present (Odoo native field still active during
            // transition) — just send the config call
            gtag('config', GA4_ID);
            return;
        }
        var s = document.createElement('script');
        s.async = true;
        s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
        document.head.appendChild(s);
        gtag('config', GA4_ID);
    }

    function updateGCM() {
        var analytics = CookieConsent.acceptedCategory('analytics');
        var marketing  = CookieConsent.acceptedCategory('marketing');
        gtag('consent', 'update', {
            analytics_storage:  analytics ? 'granted' : 'denied',
            ad_storage:         marketing ? 'granted' : 'denied',
            ad_user_data:       marketing ? 'granted' : 'denied',
            ad_personalization: marketing ? 'granted' : 'denied'
        });
    }

    // ── 3. vanilla-cookieconsent v3 init ────────────────────────────────────
    CookieConsent.run({

        guiOptions: {
            consentModal: {
                layout:             'bar inline',
                position:           'bottom',
                equalWeightButtons: true,
                flipButtons:        false
            },
            preferencesModal: {
                layout:             'box',
                equalWeightButtons: true,
                flipButtons:        false
            }
        },

        categories: {
            necessary: {
                enabled:  true,
                readOnly: true
            },
            analytics: {
                enabled: false,
                autoClear: {
                    cookies: [{ name: /^(_ga|_gid|_gat)/ }]
                }
            },
            marketing: {
                enabled: false,
                autoClear: {
                    cookies: [{ name: /^(_fbp|_fbc|fr)/ }]
                }
            }
        },

        language: {
            default: 'en',
            translations: {
                en: {
                    consentModal: {
                        title:              'We use cookies',
                        description:        'We use analytics cookies to understand how our trade portal is used, and marketing cookies for advertising. You can accept all, reject all, or set your preferences.',
                        acceptAllBtn:       'Accept all',
                        acceptNecessaryBtn: 'Reject all',
                        showPreferencesBtn: 'Manage preferences',
                        footer:             '<a href="/privacy-policy">Privacy Policy</a> · <a href="/terms">Terms</a>'
                    },
                    preferencesModal: {
                        title:              'Cookie preferences',
                        acceptAllBtn:       'Accept all',
                        acceptNecessaryBtn: 'Reject all',
                        savePreferencesBtn: 'Save preferences',
                        closeIconLabel:     'Close',
                        serviceCounterLabel: 'Service|Services',
                        sections: [
                            {
                                title:       'Strictly necessary',
                                description: 'Required for login, security, and the shopping basket. Cannot be disabled.',
                                linkedCategory: 'necessary'
                            },
                            {
                                title:       'Analytics',
                                description: 'Help us understand how trade partners use the portal (Google Analytics 4). No personal data is sold.',
                                linkedCategory: 'analytics'
                            },
                            {
                                title:       'Marketing',
                                description: 'Used for targeted advertising on Google, Instagram, and Meta. Helps us reach relevant security installers.',
                                linkedCategory: 'marketing'
                            }
                        ]
                    }
                }
            }
        },

        onConsent: function () {
            updateGCM();
            if (CookieConsent.acceptedCategory('analytics')) {
                loadGA4();
            }
        },

        onChange: function () {
            updateGCM();
            if (CookieConsent.acceptedCategory('analytics')) {
                loadGA4();
            }
        }
    });

})();
