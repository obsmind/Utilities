from . import controllers


def post_install(env):
    """
    Re-apply all site-specific view customisations after module install/upgrade.
    Targets views owned by the `website` module so they survive website module
    upgrades — upgrading trikdis_b2b re-applies everything cleanly.
    """

    # ------------------------------------------------------------------
    # 1. Header CTA — Register button for public / Shop for logged-in
    # ------------------------------------------------------------------
    hdr = env.ref('website.header_call_to_action', raise_if_not_found=False)
    if hdr:
        hdr.write({'arch': (
            '<data inherit_id="website.placeholder_header_call_to_action"'
            ' name="Header Call to Action" active="True">'
            '<xpath expr="." position="inside">'
            '<li t-attf-class="#{_item_class}">'
            '<div t-attf-class="oe_structure oe_structure_solo #{_div_class}">'
            '<section class="oe_unremovable oe_unmovable s_text_block"'
            ' data-snippet="s_text_block" data-name="Text">'
            '<div class="container">'
            '<t t-if="website.is_public_user()">'
            '<a href="/#x_register"'
            ' class="oe_unremovable btn btn-warning btn_cta fw-bold"'
            ' style="color:#1e2d5e">Register</a>'
            '</t>'
            '<t t-else="">'
            '<a href="/shop"'
            ' class="oe_unremovable btn btn-warning btn_cta fw-bold"'
            ' style="color:#1e2d5e">Shop</a>'
            '</t>'
            '</div>'
            '</section>'
            '</div>'
            '</li>'
            '</xpath>'
            '</data>'
        )})

    # ------------------------------------------------------------------
    # 2. Footer copyright span — © 2026 UAB Trikdis
    # ------------------------------------------------------------------
    cpr = env.ref('website.footer_copyright_company_name', raise_if_not_found=False)
    if cpr:
        cpr.write({'arch': (
            '<data inherit_id="website.layout">'
            '<xpath expr="//footer//span[hasclass(\'o_footer_copyright_name\')]"'
            ' position="replace">'
            '<span class="o_footer_copyright_name me-2">© 2026 UAB Trikdis</span>'
            '</xpath>'
            '</data>'
        )})

    # ------------------------------------------------------------------
    # 3. Custom footer — full dark footer with UAB Trikdis + www.trikdis.com
    # ------------------------------------------------------------------
    ftr = env.ref('website.footer_custom', raise_if_not_found=False)
    if ftr:
        ftr.write({'arch': (
            "<data inherit_id=\"website.layout\" name=\"Default\" active=\"True\">"
            "<xpath expr=\"//div[@id='footer']\" position=\"replace\">"
            "<div id=\"footer\" class=\"oe_structure oe_structure_solo\""
            " t-ignore=\"true\" t-if=\"not no_footer\">"
            "<footer style=\"background:#1a1a2e;color:#ccc;\" class=\"py-4\">"
            "<div class=\"container\">"
            "<div class=\"row g-4\">"
            "<div class=\"col-md-5\">"
            "<h6 style=\"color:white;font-weight:700;\" t-translation=\"off\">UAB Trikdis</h6>"
            "<p class=\"small mb-1\">Professional security electronics since 1995.</p>"
            "<p class=\"small mb-1\"><a href=\"mailto:uk@trikdis.lt\" style=\"color:#aab\">uk@trikdis.lt</a></p>"
            "<p class=\"small mb-1\"><a href=\"tel:03302237838\" style=\"color:#aab\" t-translation=\"off\">0330 223 7838</a></p>"
            "</div>"
            "<div class=\"col-md-4\">"
            "<h6 style=\"color:white;font-weight:700;\">Products</h6>"
            "<p class=\"small mb-1\"><a href=\"/shop\" style=\"color:#aab;text-decoration:none;\" t-translation=\"off\">GT+ Communicator</a></p>"
            "<p class=\"small mb-1\"><a href=\"/shop\" style=\"color:#aab;text-decoration:none;\" t-translation=\"off\">GET Communicator</a></p>"
            "<p class=\"small mb-1\"><a href=\"/shop\" style=\"color:#aab;text-decoration:none;\" t-translation=\"off\">Gator WiFi</a></p>"
            "<p class=\"small mb-1\"><a href=\"/shop\" style=\"color:#aab;text-decoration:none;\" t-translation=\"off\">Gator LTE</a></p>"
            "</div>"
            "<div class=\"col-md-3\">"
            "<h6 style=\"color:white;font-weight:700;\">Legal</h6>"
            "<p class=\"small mb-2\" style=\"color:#ccc;\">UK orders accepted. Invoicing via EU entity"
            " (TRIKDIS UAB, Lithuania). UK VAT registration in progress.</p>"
            "<p class=\"small\"><a href=\"https://trikdis.com/en/privacy-policy/\""
            " target=\"_blank\" rel=\"noopener\""
            " style=\"color:#aab;text-decoration:none;\">Privacy Policy</a></p>"
            "</div>"
            "</div>"
            "<hr style=\"border-color:#333;\" class=\"mt-3\"/>"
            "<p class=\"small text-center mb-0\" style=\"color:#666;\">"
            "&#169; 2026 UAB Trikdis. B2B trade portal. &#183;"
            " <a href=\"https://www.trikdis.com\" target=\"_blank\" rel=\"noopener\""
            " style=\"color:#888;\">www.trikdis.com</a>"
            "</p>"
            "</div>"
            "</footer>"
            "</div>"
            "</xpath>"
            "</data>"
        )})

    # ------------------------------------------------------------------
    # 4. Contact page — heading, lead text, sidebar company name
    # ------------------------------------------------------------------
    ctu = env.ref('website.contactus', raise_if_not_found=False)
    if ctu:
        arch = ctu.arch
        # Normalise any variant of the company name / heading
        arch = arch.replace('>Contact Trikdis UK<', '>Contact UAB Trikdis<')
        arch = arch.replace('>Contact UAB TRIKDIS<', '>Contact UAB Trikdis<')
        arch = arch.replace(
            'Questions about our alarm communicators, trade account applications, or ordering?'
            ' Get in touch — we typically respond within one business day.',
            'Direct from the manufacturer — no middleman, no ticket queue.'
            " Drop us a line and we’ll get back to you within one business day."
        )
        arch = arch.replace('>Trikdis UK<', '>UAB Trikdis<')
        arch = arch.replace('>UAB TRIKDIS<', '>UAB Trikdis<')
        ctu.write({'arch': arch})

    # ------------------------------------------------------------------
    # 5. Ensure Odoo brand promotion bar is hidden (belt + suspenders
    #    alongside the compiled CSS in static/src/css/custom.css)
    # ------------------------------------------------------------------
    website = env['website'].search([], limit=1)
    if website:
        head = website.custom_code_head or ''
        hide_css = '<style>.o_brand_promotion{display:none!important}</style>'
        if hide_css not in head:
            website.write({'custom_code_head': head + '\n' + hide_css})
