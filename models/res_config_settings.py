from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fenixtrace_upload_directory = fields.Char(
        string='FenixTrace Upload Directory',
        config_parameter='fenixtrace_odoo_connector.upload_directory'
    )
    fenixtrace_integration_kit_url = fields.Char(
        string='FenixTrace Integration Kit URL',
        config_parameter='fenixtrace_odoo_connector.integration_kit_url'
    )
