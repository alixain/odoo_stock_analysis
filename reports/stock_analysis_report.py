# Path: custom_addons/stock_analysis_report/reports/stock_analysis_report.py
from odoo import api, models
from datetime import datetime

class StockAnalysisReport(models.AbstractModel):
    _name = 'report.stock_analysis_report.stock_analysis_report_template'
    _description = 'Stock Analysis Report'

    def _get_moves_domain(self, product, date_from=False, date_to=False):
        domain = [
            ('product_id', '=', product.id),
            ('state', '=', 'done'),
        ]
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        return domain

    def _get_stock_moves(self, product, date_from=False, date_to=False):
        domain = self._get_moves_domain(product, date_from, date_to)
        return self.env['stock.move'].search(domain)

    def _get_balance_at_date(self, product, date):
        domain = self._get_moves_domain(product, date_to=date)
        moves = self.env['stock.move'].search(domain)
        
        balance = 0.0
        for move in moves:
            if move.location_dest_id.usage == 'internal' and move.location_id.usage != 'internal':
                balance += move.product_uom_qty
            elif move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal':
                balance -= move.product_uom_qty
        return balance

    def _get_in_out_qty(self, product, date_from, date_to):
        moves = self._get_stock_moves(product, date_from, date_to)
        
        in_qty = sum(moves.filtered(
            lambda m: m.location_dest_id.usage == 'internal' and 
                     m.location_id.usage != 'internal'
        ).mapped('product_uom_qty'))
        
        out_qty = sum(moves.filtered(
            lambda m: m.location_id.usage == 'internal' and 
                     m.location_dest_id.usage != 'internal'
        ).mapped('product_uom_qty'))
        
        return in_qty, out_qty

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        product_ids = data['form']['product_ids']

        products = self.env['product.product'].search([
            ('id', 'in', product_ids)] if product_ids else [('type', '=', 'product')]
        )
        
        report_data = []
        for product in products:
            # Get starting balance
            start_balance = self._get_balance_at_date(product, start_date)
            
            # Get in/out quantities
            in_qty, out_qty = self._get_in_out_qty(product, start_date, end_date)
            
            # Calculate ending balance
            end_balance = start_balance + in_qty - out_qty
            
            report_data.append({
                'product': product,
                'start_balance': start_balance,
                'in_qty': in_qty,
                'out_qty': out_qty,
                'end_balance': end_balance,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'data': data['form'],
            'report_data': report_data,
            'start_date': start_date,
            'end_date': end_date,
        }