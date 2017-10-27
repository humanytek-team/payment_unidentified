# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Rubén Bravo <rubenred18@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = 'account.payment'

    unidentified = fields.Boolean('Unidentified')
    identified_ids = fields.One2many('payment.identified',
                                        'account_payment_id',
                                        string='Identified Payments')


class PaymentIdentified(models.Model):
    _name = "payment.identified"

    @api.multi
    def calculate(self):
        if self.partner_id:
            AccountInvoice = self.env['account.invoice']
            AccountPaymentIdentified = self.env['account.payment.identified']
            AccountPaymentIdentified.search([
                ('payment_identified_id', '=', self.id)]).unlink()
            account_invoice_ids = AccountInvoice.search([
                            ('partner_id.id', '=', self.partner_id.id),
                            ('state', '=', 'open')
                            ])
            for account_invoice in account_invoice_ids:
                AccountPaymentIdentified.create({
                                    'payment_identified_id': self.id,
                                    'account_invoice_id': account_invoice.id})

        return {}

    @api.multi
    def confirm(self):
        self.state = 'done'

    partner_id = fields.Many2one('res.partner', string='Customer',
                                required=True)
    account_payment_id = fields.Many2one('account.payment', string='Payment',
                                required=False)
    account_payments_identified_ids = fields.One2many(
                                        'account.payment.identified',
                                        'payment_identified_id',
                                        string='Identified Payments')
    state = fields.Selection([
        ('draft', 'Draft'),
        #('open', 'Open'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange',
        default='draft')


class AccountPaymentIdentified(models.Model):
    _name = "account.payment.identified"

    payment_identified_id = fields.Many2one('payment.identified',
                                string='Payment',
                                required=False)
    account_invoice_id = fields.Many2one('account.invoice',
                                string='Payment',
                                required=True)
    amount = fields.Float(string='Amount')
    confirm = fields.Boolean(string='Confirm')
    account_invoice_name = fields.Char(related='account_invoice_id.move_name',
                        string='Invoice', readonly=True, store=False)
    account_invoice_date = fields.Date(
                        related='account_invoice_id.date_invoice',
                        string='Date', readonly=True, store=False)
    currency_id = fields.Many2one(
                        related='account_invoice_id.currency_id',
                        string='Currency', readonly=True, store=False)

    account_invoice_amount_total = fields.Monetary(
                        related='account_invoice_id.amount_total',
                        string='Amount Total', readonly=True, store=False)
    account_invoice_residual = fields.Monetary(
                        related='account_invoice_id.residual',
                        string='Amount of Debt', readonly=True, store=False)

