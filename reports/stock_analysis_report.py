from odoo import api, models
from datetime import datetime

class StockAnalysisReport(models.AbstractModel):
    _name = 'report.stock_analysis_report.stock_analysis_report_template'
    _description = 'Stock Analysis Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        product_ids = data['form']['product_ids']

        domain = [('product_id.type', '=', 'product')]
        if product_ids:
            domain.append(('product_id', 'in', product_ids))

        products = self.env['product.product'].search([('id', 'in', product_ids)] if product_ids else [('type', '=', 'product')])
        
        report_data = []
        for product in products:
            # Calculate starting balance
            domain_start = domain + [
                ('date', '<', start_date),
                ('product_id', '=', product.id)
            ]
            start_qty = sum(self.env['stock.move.line'].search(domain_start).mapped('qty_done'))

            # Calculate movements
            domain_moves = domain + [
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('product_id', '=', product.id)
            ]
            moves = self.env['stock.move.line'].search(domain_moves)

            in_qty = sum(moves.filtered(lambda m: m.move_id.location_dest_id.usage == 'internal').mapped('qty_done'))
            out_qty = sum(moves.filtered(lambda m: m.move_id.location_id.usage == 'internal').mapped('qty_done'))
            
            report_data.append({
                'product': product,
                'start_balance': start_qty,
                'in_qty': in_qty,
                'out_qty': out_qty,
                'end_balance': start_qty + in_qty - out_qty,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'data': data['form'],
            'report_data': report_data,
            'start_date': start_date,
            'end_date': end_date,
        }