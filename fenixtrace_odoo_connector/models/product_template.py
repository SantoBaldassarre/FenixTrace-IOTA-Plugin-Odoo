import json
import os
import re
from datetime import datetime
from urllib import error as urllib_error
from urllib import request as urllib_request

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fenixtrace_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('queued', 'Queued'),
            ('synced', 'Synced'),
            ('error', 'Error')
        ],
        default='draft',
        string='FenixTrace State',
        copy=False
    )
    fenixtrace_last_sync_at = fields.Datetime(string='FenixTrace Last Sync', copy=False)
    fenixtrace_tx_hash = fields.Char(string='FenixTrace Product Tx Hash', copy=False)
    fenixtrace_notarization_tx_hash = fields.Char(string='FenixTrace Notarization Tx Hash', copy=False)
    fenixtrace_last_file_name = fields.Char(string='FenixTrace Last File', copy=False)
    fenixtrace_last_error = fields.Text(string='FenixTrace Last Error', copy=False)

    def _build_fenixtrace_payload(self):
        self.ensure_one()
        category_name = self.categ_id.name if self.categ_id else ''
        return {
            'name': self.name or f'product-{self.id}',
            'description': self.description_sale or self.description or '',
            'category': category_name,
            'manufacturer': self.company_id.name or '',
            'defaultCode': self.default_code or '',
            'barcode': self.barcode or '',
            'listPrice': self.list_price,
            'standardPrice': self.standard_price,
            'currency': self.currency_id.name if self.currency_id else '',
            'createdAt': datetime.utcnow().isoformat() + 'Z',
            'source': 'odoo_plugin',
            'odoo': {
                'productTemplateId': self.id,
                'productName': self.name or '',
                'companyId': self.company_id.id if self.company_id else None,
                'companyName': self.company_id.name if self.company_id else ''
            }
        }

    def _generate_fenixtrace_filename(self):
        self.ensure_one()
        base_name = self.default_code or self.name or f'product-{self.id}'
        slug = re.sub(r'[^a-zA-Z0-9_-]+', '_', base_name).strip('_').lower()
        if not slug:
            slug = f'product_{self.id}'
        stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f'{slug}_{self.id}_{stamp}.json'

    def _write_payload_file(self, upload_dir, file_name, payload):
        target_path = os.path.join(upload_dir, file_name)
        with open(target_path, 'w', encoding='utf-8') as handler:
            json.dump(payload, handler, ensure_ascii=False, indent=2)
        return target_path

    def _trigger_integration_kit_process(self, base_url, file_name):
        endpoint = f"{base_url.rstrip('/')}/process/{file_name}"
        req = urllib_request.Request(
            endpoint,
            data=b'',
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            with urllib_request.urlopen(req, timeout=45) as response:
                raw = response.read().decode('utf-8') if response.readable() else '{}'
                return json.loads(raw) if raw else {}
        except urllib_error.HTTPError as exc:
            detail = exc.read().decode('utf-8') if exc.fp else str(exc)
            raise UserError(_('FenixTrace processing failed: %s') % detail) from exc
        except urllib_error.URLError as exc:
            raise UserError(_('Cannot reach Integration Kit URL: %s') % str(exc.reason)) from exc

    def _send_to_fenixtrace(self):
        self.ensure_one()
        params = self.env['ir.config_parameter'].sudo()
        upload_dir = (params.get_param('fenixtrace_odoo_connector.upload_directory') or '').strip()
        integration_kit_url = (params.get_param('fenixtrace_odoo_connector.integration_kit_url') or '').strip()

        if not upload_dir:
            raise UserError(_('Set FenixTrace Upload Directory in Settings before sending products.'))
        if not os.path.isdir(upload_dir):
            raise UserError(_('Upload directory does not exist: %s') % upload_dir)
        if not os.access(upload_dir, os.W_OK):
            raise UserError(_('Upload directory is not writable: %s') % upload_dir)
        if not integration_kit_url:
            raise UserError(_('Set FenixTrace Integration Kit URL in Settings before sending products.'))

        payload = self._build_fenixtrace_payload()
        file_name = self._generate_fenixtrace_filename()
        self._write_payload_file(upload_dir, file_name, payload)

        self.write({
            'fenixtrace_state': 'queued',
            'fenixtrace_last_file_name': file_name,
            'fenixtrace_last_error': False
        })

        response_data = self._trigger_integration_kit_process(integration_kit_url, file_name)
        result_data = response_data.get('result') if isinstance(response_data, dict) else None
        result_data = result_data if isinstance(result_data, dict) else {}

        self.write({
            'fenixtrace_state': 'synced',
            'fenixtrace_tx_hash': result_data.get('txHash') or '',
            'fenixtrace_notarization_tx_hash': result_data.get('notarizationTxHash') or '',
            'fenixtrace_last_sync_at': fields.Datetime.now(),
            'fenixtrace_last_error': False
        })
        return result_data

    def action_send_to_fenixtrace(self):
        self.ensure_one()
        self._send_to_fenixtrace()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('FenixTrace'),
                'message': _('Product sent and notarization queued successfully.'),
                'type': 'success',
                'sticky': False
            }
        }

    def action_send_to_fenixtrace_batch(self):
        success_count = 0
        error_count = 0
        errors = []
        for record in self:
            try:
                record._send_to_fenixtrace()
                success_count += 1
            except Exception as exc:
                error_count += 1
                record.write({
                    'fenixtrace_state': 'error',
                    'fenixtrace_last_error': str(exc)
                })
                errors.append(record.display_name or str(record.id))
        if error_count:
            message = _('Processed %s products, %s errors.') % (success_count, error_count)
            if errors:
                message = f"{message} {', '.join(errors)}"
            notification_type = 'warning'
        else:
            message = _('Processed %s products successfully.') % success_count
            notification_type = 'success'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('FenixTrace Batch'),
                'message': message,
                'type': notification_type,
                'sticky': False
            }
        }
