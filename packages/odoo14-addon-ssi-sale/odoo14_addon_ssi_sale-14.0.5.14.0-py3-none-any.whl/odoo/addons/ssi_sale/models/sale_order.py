# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = [
        "sale.order",
        "mixin.policy",
        "mixin.many2one_configurator",
        "mixin.sequence",
        "mixin.print_document",
        "mixin.multiple_approval",
    ]
    _document_number_field = "name"
    _automatically_insert_print_button = True

    _approval_state_field = "state"
    _approval_from_state = "draft"
    _approval_to_state = "sale"
    _approval_cancel_state = "cancel"
    _approval_reject_state = "reject"
    _approval_state = "confirm"
    _after_approved_method = "action_confirm"
    _automatically_insert_multiple_approval_page = True
    _multiple_approval_xpath_reference = "//page[last()]"

    def _compute_policy(self):
        _super = super()
        _super._compute_policy()

    @api.depends(
        "type_id",
    )
    def _compute_allowed_pricelist_ids(self):
        for record in self:
            result = False
            if record.type_id:
                result = record._m2o_configurator_get_filter(
                    object_name="product.pricelist",
                    method_selection=record.type_id.pricelist_selection_method,
                    manual_recordset=record.type_id.pricelist_ids,
                    domain=record.type_id.pricelist_domain,
                    python_code=record.type_id.pricelist_python_code,
                )
            record.allowed_pricelist_ids = result

    allowed_pricelist_ids = fields.Many2many(
        comodel_name="product.pricelist",
        string="Allowed Pricelists",
        compute="_compute_allowed_pricelist_ids",
        store=False,
        compute_sudo=True,
    )
    type_id = fields.Many2one(
        comodel_name="sale_order_type",
        string="Type",
        required=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        },
    )

    total_qty = fields.Float(
        string="Total Qty",
        compute="_compute_total_qty",
        store=True,
        compute_sudo=True,
    )
    qty_to_deliver = fields.Float(
        string="Qty to Deliver",
        compute="_compute_qty_deliver",
        store=True,
        compute_sudo=True,
    )
    qty_delivered = fields.Float(
        string="Qty Delivered",
        compute="_compute_qty_deliver",
        store=True,
        compute_sudo=True,
    )
    percent_delivered = fields.Float(
        string="Percent Delivered",
        compute="_compute_qty_deliver",
        store=True,
        compute_sudo=True,
    )
    qty_invoiced = fields.Float(
        string="Qty Invoiced",
        compute="_compute_qty_invoice",
        store=True,
        compute_sudo=True,
    )
    percent_invoiced = fields.Float(
        string="Percent Invoiced",
        compute="_compute_qty_invoice",
        store=True,
        compute_sudo=True,
    )
    amount_invoice = fields.Monetary(
        string="Amount Invoiced",
        compute="_compute_qty_invoice",
        store=True,
        compute_sudo=True,
    )
    amount_uninvoice = fields.Monetary(
        string="Amount Uninvoiced",
        compute="_compute_qty_invoice",
        store=True,
        compute_sudo=True,
    )
    amount_delivered = fields.Monetary(
        string="Amount Delivered",
        compute="_compute_qty_deliver",
        store=True,
        compute_sudo=True,
    )
    amount_undelivered = fields.Monetary(
        string="Amount Undelivered",
        compute="_compute_qty_deliver",
        store=True,
        compute_sudo=True,
    )

    # We want to restrict order line modificarion only on draft state
    order_line = fields.One2many(
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    revenue_with_tax = fields.Float(
        string="Revenue With Tax",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )
    revenue_without_tax = fields.Float(
        string="Revenue Without Tax",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )
    product_cost = fields.Float(
        string="Product Cost",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )
    profit_with_tax = fields.Float(
        string="Profit With Tax",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )
    profit_without_tax = fields.Float(
        string="Profit Without Tax",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )

    # Fields for policy mixin
    capture_ok = fields.Boolean(
        string="Can Capture Transaction",
        compute="_compute_policy",
        compute_sudo=True,
    )
    void_ok = fields.Boolean(
        string="Can Void Transaction",
        compute="_compute_policy",
        compute_sudo=True,
    )
    invoice_ok = fields.Boolean(
        string="Can Create Invoice",
        compute="_compute_policy",
        compute_sudo=True,
    )
    email_ok = fields.Boolean(
        string="Can Send by Email",
        compute="_compute_policy",
        compute_sudo=True,
    )
    proforma_ok = fields.Boolean(
        string="Can Send PRO-FORMA Invoice",
        compute="_compute_policy",
        compute_sudo=True,
    )
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
        compute_sudo=True,
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
        compute_sudo=True,
    )
    draft_ok = fields.Boolean(
        string="Can Set to Quotation",
        compute="_compute_policy",
        compute_sudo=True,
    )
    done_ok = fields.Boolean(
        string="Can Lock",
        compute="_compute_policy",
        compute_sudo=True,
    )
    unlock_ok = fields.Boolean(
        string="Can Unlock",
        compute="_compute_policy",
        compute_sudo=True,
    )
    manual_number_ok = fields.Boolean(
        string="Can Input Manual Document Number",
        compute="_compute_policy",
        compute_sudo=True,
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
        compute_sudo=True,
    )
    reject_ok = fields.Boolean(
        string="Can Reject",
        compute="_compute_policy",
        compute_sudo=True,
    )
    restart_approval_ok = fields.Boolean(
        string="Can Restart Approval",
        compute="_compute_policy",
        compute_sudo=True,
    )
    state = fields.Selection(
        selection_add=[
            ("draft",),
            ("confirm", "Waiting for Approval"),
            ("reject", "Rejected"),
        ],
        ondelete={
            "confirm": "set default",
            "reject": "set default",
        },
    )

    @api.depends(
        "order_line",
        "order_line.product_cost",
        "order_line.revenue_without_tax",
        "order_line.revenue_with_tax",
    )
    def _compute_product_cost(self):
        for record in self:
            cost = revenue_without_tax = revenue_with_tax = 0.0
            for line in record.order_line:
                cost += line.product_cost
                revenue_without_tax += line.revenue_without_tax
                revenue_with_tax += line.revenue_with_tax

            record.product_cost = cost
            record.revenue_without_tax = revenue_without_tax
            record.revenue_with_tax = revenue_with_tax
            record.profit_without_tax = revenue_without_tax - cost
            record.profit_with_tax = revenue_with_tax - cost

    @api.depends(
        "order_line",
        "order_line.product_type",
        "order_line.product_uom_qty",
        "order_line.qty_delivered",
    )
    def _compute_qty_deliver(self):
        for record in self:
            qty_to_deliver = qty_delivered = percent_delivered = amount_delivered = (
                amount_undelivered
            ) = 0.0
            for line in record.order_line:
                if line.product_id.type == "product" and line.product_type == "product":
                    qty_to_deliver += line.qty_to_deliver
                    qty_delivered += line.qty_delivered
                    amount_delivered += line.amount_delivered
                    amount_undelivered += line.amount_undelivered
            try:
                percent_delivered = qty_delivered / record.total_qty
            except ZeroDivisionError:
                percent_delivered = 0.0
            record.qty_to_deliver = qty_to_deliver
            record.qty_delivered = qty_delivered
            record.percent_delivered = percent_delivered
            record.amount_delivered = amount_delivered
            record.amount_undelivered = amount_undelivered

    @api.depends(
        "order_line",
        "order_line.product_type",
        "order_line.product_uom_qty",
        "order_line.qty_invoiced",
        "total_qty",
    )
    def _compute_qty_invoice(self):
        for record in self:
            qty_invoiced = percent_invoiced = amount_invoice = amount_uninvoice = 0.0
            for line in record.order_line:
                qty_invoiced += line.qty_invoiced
                amount_invoice += line.amount_invoice
                amount_uninvoice += line.amount_uninvoice
            if record.total_qty != 0.0:
                try:
                    percent_invoiced = qty_invoiced / record.total_qty
                except ZeroDivisionError:
                    percent_invoiced = 0.0

            record.qty_invoiced = qty_invoiced
            record.percent_invoiced = percent_invoiced
            record.amount_invoice = amount_invoice
            record.amount_uninvoice = amount_uninvoice

    @api.depends(
        "order_line",
        "order_line.product_uom_qty",
    )
    def _compute_total_qty(self):
        for record in self:
            result = 0.0
            for line in record.order_line:
                result += line.product_uom_qty
            record.total_qty = result

    def action_confirm(self):
        _super = super()
        for record in self:
            record._create_sequence()
        res = _super.action_confirm()
        return res

    def action_confirm_custom(self):
        for record in self.sudo():
            record.write(
                {
                    "state": "confirm",
                }
            )
            record.action_request_approval()

    def action_recompute_qty_helper(self):
        for record in self.sudo():
            record.order_line._get_to_invoice_qty()
            record.order_line._compute_qty_delivered()
            record.order_line._compute_percent_delivered()
            record.order_line._compute_percent_invoiced()
            record._compute_qty_invoice()
            record._compute_qty_deliver()

    @api.model
    def default_get(self, fields):
        _super = super()
        res = _super.default_get(fields)

        res["name"] = "/"

        return res

    @api.model
    def create(self, vals):
        vals["name"] = "/"
        _super = super()
        res = _super.create(vals)
        return res

    @api.model
    def _get_policy_field(self):
        res = super()._get_policy_field()
        policy_field = [
            "capture_ok",
            "void_ok",
            "invoice_ok",
            "email_ok",
            "proforma_ok",
            "confirm_ok",
            "cancel_ok",
            "draft_ok",
            "done_ok",
            "unlock_ok",
            "manual_number_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
        ]
        res += policy_field
        return res

    @api.onchange(
        "type_id",
        "partner_id",
    )
    def onchange_pricelist_id(self):
        if self.user_has_groups("product.group_product_pricelist"):
            self.pricelist_id = False
            if self.type_id and self.partner_id:
                if (
                    self.partner_id.property_product_pricelist.id
                    in self.allowed_pricelist_ids.ids
                ):
                    self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.constrains(
        "name",
    )
    def _constrains_duplicate_document_number(self):
        for record in self.sudo():
            if not record._check_duplicate_document_number():
                error_message = """
                Document Type: %s
                Context: Change document number
                Database ID: %s
                Problem: Duplicate document number
                Solution: Change document number into different number
                """ % (
                    self._description.lower(),
                    record.id,
                )
                raise UserError(_(error_message))

    def name_get(self):
        result = []
        for record in self:
            if getattr(record, self._document_number_field) == "/":
                name = "*" + str(record.id)
            else:
                name = record.name
            result.append((record.id, name))
        return result

    def _prepare_confirmation_values(self):
        res = super()._prepare_confirmation_values()
        if "date_order" in res:
            del res["date_order"]
        return res

    def _check_duplicate_document_number(self):
        self.ensure_one()
        result = True
        criteria = [
            (
                "name",
                "=",
                self.name,
            ),
            ("name", "!=", "/"),
            ("id", "!=", self.id),
        ]
        SaleOrder = self.env["sale.order"]
        count_duplicate = SaleOrder.search_count(criteria)
        if count_duplicate > 0:
            result = False
        return result
