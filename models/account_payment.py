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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = 'account.payment'

    unidentified = fields.Boolean('Unidentified')
    identified = fields.Boolean('Identified')
    identified_ids = fields.One2many('payment.identified',
                                        'account_payment_id',
                                        string='Identified Payments')
    amount_identified = fields.Float('Identified Amount',
                        compute='_compute_amount_identified', readonly=True)
    amount_unidentified = fields.Float('Unidentified Amount',
                        compute='_compute_amount_unidentified', readonly=True)
    payment_unidentified_id = fields.Many2one('account.payment',
                                    string='Unidentified ')

    @api.one
    def _compute_amount_identified(self):
        self.amount_identified = sum([identified.amount_identified
                                for identified in
                                self.identified_ids
                                if identified.state == 'done'])

    @api.one
    def _compute_amount_unidentified(self):
        self.amount_unidentified = self.amount - self.amount_identified

    def _create_payment_entry(self, amount):
        move = super(AccountPayment, self)._create_payment_entry(amount)
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
        if self.unidentified:
            aml_dict = self._get_shared_move_line_unidentified(debit, credit, amount_currency, move.id, False)
            aml_dict.update(self._get_counterpart_move_line_unidentified())
            aml_dict.update({'currency_id': currency_id})
            aml = aml_obj.create(aml_dict)

            counterpart_aml_dict = self._get_shared_move_line_unidentified(credit, debit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_move_line_unidentified())
            counterpart_aml_dict.update({'currency_id': currency_id})
            counterpart_aml = aml_obj.create(counterpart_aml_dict)
        if self.identified:
            _logger.info('MOOOOOOOOOOOOOOOOOOOOOVEEEEEEEEEEEEEEEEEEEE')
            _logger.info(move)
            _logger.info('MOOOOOOOOOOOOOOOOOOOOOVEEEEEEEEEEEEEEEEEEEElineeeee')
            _logger.info(move.line_ids)
            #aml.write({'account_id': self.destination_account_id.id})
            #aml.write({'partner_id': self.payment_unidentified_id.partner_id.id})

        #""" Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            #Return the journal entry.
        #"""
        #aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        #invoice_currency = False
        #if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            ##if all the invoices selected share the same currency, record the paiement in that currency too
            #invoice_currency = self.invoice_ids[0].currency_id
        #debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        #move = self.env['account.move'].create(self._get_move_vals())

        ##Write line corresponding to invoice payment

        #counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        #counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        #counterpart_aml_dict.update({'currency_id': currency_id})
        #counterpart_aml = aml_obj.create(counterpart_aml_dict)
        ##Reconcile with the invoices
        #if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            #writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            #amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            ## the writeoff debit and credit must be computed from the invoice residual in company currency
            ## minus the payment amount in company currency, and not from the payment difference in the payment currency
            ## to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            #total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            #total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            #if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                #amount_wo = total_payment_company_signed - total_residual_company_signed
            #else:
                #amount_wo = total_residual_company_signed - total_payment_company_signed
            ## Align the sign of the secondary currency writeoff amount with the sign of the writeoff
            ## amount in the company currency
            #if amount_wo > 0:
                #debit_wo = amount_wo
                #credit_wo = 0.0
                #amount_currency_wo = abs(amount_currency_wo)
            #else:
                #debit_wo = 0.0
                #credit_wo = -amount_wo
                #amount_currency_wo = -abs(amount_currency_wo)
            #writeoff_line['name'] = _('Counterpart')
            #writeoff_line['account_id'] = self.writeoff_account_id.id
            #writeoff_line['debit'] = debit_wo
            #writeoff_line['credit'] = credit_wo
            #writeoff_line['amount_currency'] = amount_currency_wo
            #writeoff_line['currency_id'] = currency_id
            #writeoff_line = aml_obj.create(writeoff_line)
            #if counterpart_aml['debit']:
                #counterpart_aml['debit'] += credit_wo - debit_wo
            #if counterpart_aml['credit']:
                #counterpart_aml['credit'] += debit_wo - credit_wo
            #counterpart_aml['amount_currency'] -= amount_currency_wo
        #self.invoice_ids.register_payment(counterpart_aml)

        ##Write counterpart lines
        #if not self.currency_id != self.company_id.currency_id:
            #amount_currency = 0
        #liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        #liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        #aml_obj.create(liquidity_aml_dict)
        ##aml = aml_obj.create(liquidity_aml_dict)

        ##if self.identified:
            ##aml.write({'account_id': self.destination_account_id.id})
            ##aml.write({'partner_id': self.payment_unidentified_id.partner_id.id})
        ##if self.unidentified:
            ##aml_dict = self._get_shared_move_line_unidentified(debit, credit, amount_currency, move.id, False)
            ##aml_dict.update(self._get_counterpart_move_line_unidentified())
            ##aml_dict.update({'currency_id': currency_id})
            ##aml = aml_obj.create(aml_dict)

            ##counterpart_aml_dict = self._get_shared_move_line_unidentified(credit, debit, amount_currency, move.id, False)
            ##counterpart_aml_dict.update(self._get_move_line_unidentified())
            ##counterpart_aml_dict.update({'currency_id': currency_id})
            ##counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #move.post()
        return move


    def _get_shared_move_line_unidentified(self, debit, credit, amount_currency, move_id, invoice_id=False):
        return {
            'partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': False,
            'move_id': move_id,
            'debit': (debit / 1.16) * 0.16,
            'credit': (credit / 1.16 ) * 0.16,
            'amount_currency': (amount_currency / 1.16) * 0.16 or False,
        }

    def _get_move_line_unidentified(self, invoice=False):
        name = ''
        if self.partner_type == 'customer':
            if self.payment_type == 'inbound':
                name += _("Customer Payment")
            elif self.payment_type == 'outbound':
                name += _("Customer Refund")
        return {
            'name': name,
            'account_id': self.partner_id.account_tax_receivable_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }

    def _get_counterpart_move_line_unidentified(self, invoice=False):
        name = ''
        if self.partner_type == 'customer':
            if self.payment_type == 'inbound':
                name += _("Customer Payment")
            elif self.payment_type == 'outbound':
                name += _("Customer Refund")
        return {
            'name': name,
            'account_id': self.partner_id.account_tax__received_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }


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
                            ('state', '=', 'open'),
                            ('type', '=', 'out_invoice')
                            ])
            for account_invoice in account_invoice_ids:
                AccountPaymentIdentified.create({
                                    'payment_identified_id': self.id,
                                    'account_invoice_id': account_invoice.id})

        return {}

    @api.multi
    def confirm(self):
        if self.amount_identified > self.account_payment_id.amount_unidentified:
            raise ValidationError(_('The amount must not exceed the amount identified'))
        AccountPayment = self.env['account.payment']
        for account_payments_identified in self.account_payments_identified_ids:
            if account_payments_identified.confirm and account_payments_identified.amount > 0:
                ac = AccountPayment.create({'partner_id': self.partner_id.id,
                        'amount': account_payments_identified.amount,
                        'payment_date': self.account_payment_id.payment_date,
                        'identified': True,
                        'payment_type': 'inbound',
                        'journal_id': self.account_payment_id.journal_id.id,
                        'partner_type': 'customer',
                        'payment_method_id': self.account_payment_id.journal_id.inbound_payment_method_ids[0].id,
                        'invoice_ids': [(4, account_payments_identified.account_invoice_id.id)],
                        'payment_unidentified_id': self.account_payment_id.id,
                        })
                ac.post()
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
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange',
        default='draft')
    amount_identified = fields.Float('Identified Amount',
                            compute='_compute_amount_identified', readonly=True)

    @api.one
    def _compute_amount_identified(self):
        self.amount_identified = sum([account_payments_identified.amount
                                for account_payments_identified in
                                self.account_payments_identified_ids
                                if account_payments_identified.confirm])


class AccountPaymentIdentified(models.Model):
    _name = "account.payment.identified"

    @api.multi
    @api.depends('account_invoice_residual')
    @api.onchange('amount')
    def onchange_amount(self):
        if self.amount > self.account_invoice_residual:
            self.amount = self.account_invoice_residual
        return {}

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

