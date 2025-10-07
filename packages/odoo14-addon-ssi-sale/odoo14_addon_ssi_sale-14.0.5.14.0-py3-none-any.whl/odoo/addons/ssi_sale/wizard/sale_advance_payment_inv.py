from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        invoice_status = self.env.context.get("invoice_status")
        if invoice_status == "no":
            vals["advance_payment_method"] = "percentage"
        return vals
