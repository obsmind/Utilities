"""Trikdis B2B registration + contact form endpoints."""
import json
import re
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.account.controllers.terms import TermsController


# ---------------------------------------------------------------------------
# Postcode validation helpers
# ---------------------------------------------------------------------------

# Prefixes that fall outside Great Britain (Northern Ireland, Channel Islands,
# Isle of Man).  We block these at checkout address save.
_BLOCKED_POSTCODE_PREFIXES = re.compile(
    r'^(BT|GY|JE|IM)\d',
    re.IGNORECASE,
)

BLOCKED_TERRITORY_MSG = (
    "Sorry, we currently only deliver within Great Britain (England, Scotland "
    "and Wales). We do not accept orders for Northern Ireland (BT), "
    "the Channel Islands (GY/JE), or the Isle of Man (IM). "
    "Please contact us at hello@uk.trikdis.com if you have a query."
)


def _postcode_blocked(postcode: str) -> bool:
    """Return True if the postcode prefix is in a non-GB territory."""
    return bool(_BLOCKED_POSTCODE_PREFIXES.match((postcode or '').strip()))


# ---------------------------------------------------------------------------
# /terms — serve our custom Terms & Conditions page
# ---------------------------------------------------------------------------

class TrikdisTermsController(TermsController):
    """Override the account module's /terms route to serve our T&C page."""

    @http.route('/terms', type='http', auth='public', website=True)
    def terms_conditions(self, **kwargs):
        return request.render('trikdis_b2b.terms_page', {})


# ---------------------------------------------------------------------------
# Checkout address override — postcode gate
# ---------------------------------------------------------------------------

class TrikdisWebsiteSale(WebsiteSale):
    """Extend website_sale checkout to block unsupported delivery territories."""

    @http.route(
        '/shop/address/submit',
        type='http',
        methods=['POST'],
        auth='public',
        website=True,
        sitemap=False,
    )
    def shop_address_submit(self, **form_data):
        """Validate postcode before saving the address."""
        zip_code = (form_data.get('zip') or '').strip()
        if _postcode_blocked(zip_code):
            return json.dumps({
                'invalid_fields': ['zip'],
                'messages': [BLOCKED_TERRITORY_MSG],
            })
        return super().shop_address_submit(**form_data)


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------

def _applicant_confirmation_html(name, company_name, email, phone, company_reg):
    """Return branded HTML confirmation email for a trade account applicant."""
    phone_display = phone or 'n/a'
    reg_display = company_reg or 'n/a'
    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="x-apple-disable-message-reformatting">
  <style type="text/css">
    body {{ margin:0; padding:0; background-color:#f6f8f9; }}
    body, table, td, p, a {{ font-family:'Poppins',Arial,sans-serif; }}
    table td {{ border-collapse:collapse; }}
    table {{ border-spacing:0; border-collapse:collapse; }}
    img {{ border:0; outline:none; text-decoration:none; display:block; }}
    a[href^=tel] {{ color:inherit; text-decoration:none; }}
    @media only screen and (max-width:640px) {{
      .email-wrap {{ width:100% !important; }}
    }}
  </style>
</head>
<body style="margin:0; padding:0; background-color:#f6f8f9;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f6f8f9">
    <tr>
      <td align="center" style="padding:30px 0;">
        <table class="email-wrap" width="640" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="width:640px; max-width:640px;">

          <!-- LOGO -->
          <tr>
            <td align="center" bgcolor="#ffffff" style="padding:36px 40px 24px 40px;">
              <a href="https://uk.trikdis.com" target="_blank">
                <img src="https://bucket.mlcdn.com/a/485/485155/images/36527041943845c4d8e25db6ecc891767c130ce7.png" width="100" alt="Trikdis">
              </a>
            </td>
          </tr>

          <!-- DIVIDER -->
          <tr>
            <td style="padding:0 40px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr><td style="border-top:1px solid #ededf3;"></td></tr>
              </table>
            </td>
          </tr>

          <!-- HEADLINE -->
          <tr>
            <td align="center" style="padding:32px 40px 4px 40px;">
              <p style="margin:0; font-size:13px; font-weight:400; color:#a52834; line-height:150%;">Trikdis UK Trade Account</p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding:8px 40px 24px 40px;">
              <h1 style="margin:0; font-size:26px; font-weight:700; color:#111111; line-height:140%;">Your account is ready</h1>
            </td>
          </tr>

          <!-- BODY -->
          <tr>
            <td style="padding:0 40px 24px 40px;">
              <p style="margin:0 0 16px 0; font-size:14px; color:#6f6f6f; line-height:160%;">Hi {name},</p>
              <p style="margin:0 0 16px 0; font-size:14px; color:#6f6f6f; line-height:160%;">
                Your <strong style="color:#111111;">Trikdis UK trade account</strong> for
                <strong style="color:#111111;">{company_name}</strong> has been created and
                <strong style="color:#111111;">Standard Trade pricing</strong> is already applied.
              </p>
              <p style="margin:0; font-size:14px; color:#6f6f6f; line-height:160%;">
                Check your inbox for a separate email to set your password — once done, you can
                log in and place orders straight away.
              </p>
            </td>
          </tr>

          <!-- SUMMARY TABLE -->
          <tr>
            <td style="padding:0 40px 32px 40px;">
              <p style="margin:0 0 12px 0; font-size:11px; font-weight:700; color:#111111; letter-spacing:0.06em; text-transform:uppercase;">Your account details</p>
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #ededf3;">
                <tr>
                  <td width="38%" bgcolor="#f6f8f9" style="padding:10px 16px; font-size:12px; font-weight:600; color:#111111; border-bottom:1px solid #ededf3;">Company</td>
                  <td bgcolor="#ffffff" style="padding:10px 16px; font-size:12px; color:#6f6f6f; border-bottom:1px solid #ededf3;">{company_name}</td>
                </tr>
                <tr>
                  <td bgcolor="#f6f8f9" style="padding:10px 16px; font-size:12px; font-weight:600; color:#111111; border-bottom:1px solid #ededf3;">Name</td>
                  <td bgcolor="#ffffff" style="padding:10px 16px; font-size:12px; color:#6f6f6f; border-bottom:1px solid #ededf3;">{name}</td>
                </tr>
                <tr>
                  <td bgcolor="#f6f8f9" style="padding:10px 16px; font-size:12px; font-weight:600; color:#111111; border-bottom:1px solid #ededf3;">Email</td>
                  <td bgcolor="#ffffff" style="padding:10px 16px; font-size:12px; color:#6f6f6f; border-bottom:1px solid #ededf3;">{email}</td>
                </tr>
                <tr>
                  <td bgcolor="#f6f8f9" style="padding:10px 16px; font-size:12px; font-weight:600; color:#111111; border-bottom:1px solid #ededf3;">Phone</td>
                  <td bgcolor="#ffffff" style="padding:10px 16px; font-size:12px; color:#6f6f6f; border-bottom:1px solid #ededf3;">{phone_display}</td>
                </tr>
                <tr>
                  <td bgcolor="#f6f8f9" style="padding:10px 16px; font-size:12px; font-weight:600; color:#111111;">Companies House</td>
                  <td bgcolor="#ffffff" style="padding:10px 16px; font-size:12px; color:#6f6f6f;">{reg_display}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA BUTTON -->
          <tr>
            <td align="center" style="padding:0 40px 36px 40px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center" bgcolor="#a52834" style="border-radius:3px; padding:14px 32px;">
                    <a href="https://uk.trikdis.com" target="_blank"
                       style="font-size:14px; font-weight:600; color:#ffffff; text-decoration:none;">
                      Browse our products
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- DIVIDER -->
          <tr>
            <td style="padding:0 40px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr><td style="border-top:1px solid #ededf3;"></td></tr>
              </table>
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="padding:24px 40px 32px 40px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td valign="top" width="50%">
                    <p style="margin:0 0 4px 0; font-size:13px; font-weight:700; color:#111111;">Trikdis UK</p>
                    <p style="margin:0 0 14px 0; font-size:12px; color:#6f6f6f; line-height:160%;">TRIKDIS UAB &middot; Draugyst&#279;s g.&nbsp;17<br>Kaunas, Lithuania</p>
                    <table cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="padding-right:8px;">
                          <a href="https://www.facebook.com/trikdis.official" target="_blank">
                            <img src="https://assets.mlcdn.com/ml/images/icons/default/round/black/facebook.png" width="22" alt="Facebook">
                          </a>
                        </td>
                        <td style="padding-right:8px;">
                          <a href="https://www.youtube.com/channel/UCitTMmIkyy-96dJ7yDizXvg" target="_blank">
                            <img src="https://assets.mlcdn.com/ml/images/icons/default/round/black/youtube.png" width="22" alt="YouTube">
                          </a>
                        </td>
                        <td>
                          <a href="https://www.linkedin.com/company/3038024/" target="_blank">
                            <img src="https://assets.mlcdn.com/ml/images/icons/default/round/black/linkedin.png" width="22" alt="LinkedIn">
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td valign="top" width="50%" align="right">
                    <p style="margin:0 0 4px 0; font-size:12px; color:#6f6f6f; line-height:160%;">
                      Questions? Reply to this email or<br>
                      call <a href="tel:03302237838" style="color:#6f6f6f; text-decoration:none;">0330 223 7838</a>
                    </p>
                    <p style="margin:14px 0 0 0; font-size:11px; color:#aaaaaa; line-height:150%;">
                      You received this email because you submitted<br>
                      a trade account application at<br>
                      <a href="https://uk.trikdis.com" style="color:#aaaaaa; text-decoration:none;">uk.trikdis.com</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


class B2BRegister(http.Controller):

    @http.route('/b2b/register', type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def b2b_register(self, **post):
        company_name     = post.get('company_name', '').strip()
        name             = post.get('name', '').strip()
        email            = post.get('email', '').strip()
        phone            = post.get('phone', '').strip()
        job_title        = post.get('job_title', '').strip()
        company_reg      = post.get('company_reg', '').strip()
        source           = post.get('source', 'other')
        is_installer     = post.get('is_installer') == '1'
        password         = post.get('password', '')
        password_confirm = post.get('password_confirm', '')

        source_labels = {
            'show': 'The Security Event (Birmingham)',
            'referral': 'Referral',
            'search': 'Online search',
            'other': 'Other',
        }

        if not (company_name and name and email and is_installer):
            return request.redirect('/?error=missing_fields')
        if not password or len(password) < 8:
            return request.redirect('/?error=password_too_short')
        if password != password_confirm:
            return request.redirect('/?error=password_mismatch')

        env = request.env
        STANDARD_TRADE_PRICELIST_ID = 2  # Standard Trade pricelist

        # ── 1. Find or create the partner ─────────────────────────────────
        User = env['res.users'].sudo()
        Partner = env['res.partner'].sudo()

        existing_user = User.search([('login', '=', email)], limit=1)

        if existing_user:
            # Already registered — just resend set-password and continue
            portal_user = existing_user
        else:
            # Find existing partner (without a user) or create a new one
            existing_partner = Partner.search([('email', '=', email)], limit=1)
            if existing_partner:
                partner = existing_partner
            else:
                partner = Partner.create({
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'company_name': company_name,
                    'function': job_title,
                    'comment': (
                        f"B2B Trade Application\n"
                        f"Company: {company_name}\n"
                        f"Reg No: {company_reg or 'n/a'}\n"
                        f"Source: {source_labels.get(source, source)}\n"
                        f"Installer confirmed: {is_installer}"
                    ),
                    'active': True,
                })

            # ── 2. Assign Standard Trade pricelist ─────────────────────────
            try:
                pricelist = env['product.pricelist'].sudo().browse(STANDARD_TRADE_PRICELIST_ID)
                partner.property_product_pricelist = pricelist
                partner.customer_rank = 1
            except Exception:
                pass

            # ── 3. Create portal user (no auto-password email yet) ─────────
            portal_group_id = env.ref('base.group_portal').id
            portal_user = User.with_context(no_reset_password=True).create({
                'name': name,
                'login': email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [portal_group_id])],
            })

        # ── 4. Set the password directly ───────────────────────────────────
        try:
            portal_user.write({'password': password})
        except Exception:
            pass

        Mail = env['mail.mail'].sudo()

        # ── 5. Notify uk@trikdis.lt ────────────────────────────────────────
        try:
            Mail.create({
                'subject': f'New Trade Account — {company_name} (auto-approved)',
                'body_html': (
                    f"<p><strong>New B2B trade account created automatically:</strong></p>"
                    f"<ul>"
                    f"<li><b>Company:</b> {company_name}</li>"
                    f"<li><b>Name:</b> {name}</li>"
                    f"<li><b>Email:</b> {email}</li>"
                    f"<li><b>Phone:</b> {phone or 'n/a'}</li>"
                    f"<li><b>Job title:</b> {job_title or 'n/a'}</li>"
                    f"<li><b>Reg No:</b> {company_reg or 'n/a'}</li>"
                    f"<li><b>Source:</b> {source_labels.get(source, source)}</li>"
                    f"</ul>"
                    f"<p>Portal access and Standard Trade pricelist assigned automatically. "
                    f"Set-password email sent to {email}.</p>"
                ),
                'email_from': 'Trikdis UK <hello@uk.trikdis.com>',
                'email_to': 'uk@trikdis.lt',
                'auto_delete': True,
            }).send()
        except Exception:
            pass

        # ── 6. Confirmation email to the registrant ────────────────────────
        try:
            Mail.create({
                'subject': 'Your Trikdis UK Trade Account is Ready',
                'body_html': _applicant_confirmation_html(name, company_name, email, phone, company_reg),
                'email_from': 'Trikdis UK <hello@uk.trikdis.com>',
                'email_to': email,
                'auto_delete': True,
            }).send()
        except Exception:
            pass

        # ── 7. Commit, then auto-login, then go straight to the shop ──────
        # Must commit before authenticate — the new user/password must be
        # visible to the separate DB cursor opened by session.authenticate.
        env.cr.commit()
        try:
            request.session.authenticate(request.db, {
                'type': 'password',
                'login': email,
                'password': password,
            })
        except Exception:
            pass
        return request.redirect('/shop')

    @http.route('/b2b/thank-you', type='http', auth='public', website=True)
    def b2b_thankyou(self, **kw):
        return request.render('trikdis_b2b.thank_you')

    @http.route('/contactus/submit', type='http', auth='public', methods=['POST'], csrf=True, website=True)
    def contactus_submit(self, **post):
        name        = post.get('name', '').strip()
        email       = post.get('email_from', '').strip()
        phone       = post.get('phone', '').strip()
        company     = post.get('company', '').strip()
        subject     = post.get('subject', '').strip()
        description = post.get('description', '').strip()

        if not (name and email and subject and description):
            return request.redirect('/contactus?error=missing_fields')

        try:
            rows = ''
            if phone:
                rows += f'<tr><td style="color:#666;padding:2px 12px 2px 0">Phone</td><td>{phone}</td></tr>'
            if company:
                rows += f'<tr><td style="color:#666;padding:2px 12px 2px 0">Company</td><td>{company}</td></tr>'

            request.env['mail.mail'].sudo().create({
                'subject': f'Contact form: {subject}',
                'body_html': (
                    f'<p><strong>Message via uk.trikdis.com contact form</strong></p>'
                    f'<table style="font-size:14px;border-collapse:collapse">'
                    f'<tr><td style="color:#666;padding:2px 12px 2px 0">From</td><td>{name}</td></tr>'
                    f'<tr><td style="color:#666;padding:2px 12px 2px 0">Email</td>'
                    f'<td><a href="mailto:{email}">{email}</a></td></tr>'
                    f'{rows}'
                    f'</table>'
                    f'<hr style="margin:16px 0">'
                    f'<p style="white-space:pre-wrap">{description}</p>'
                    f'<hr style="margin:16px 0">'
                    f'<p style="color:#999;font-size:12px">Reply directly to this email to respond to {name}.</p>'
                ),
                'email_from': 'Trikdis UK <hello@uk.trikdis.com>',
                'email_to': 'uk@trikdis.lt',
                'auto_delete': True,
            }).send()
        except Exception:
            pass

        return request.redirect('/contactus-thank-you')
