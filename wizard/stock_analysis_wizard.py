from odoo import api, fields, models
from datetime import datetime

class StockAnalysisWizard(models.TransientModel):
    _name = 'stock.analysis.wizard'
    _description = 'Stock Analysis Report Wizard'

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    product_ids = fields.Many2many('product.product', string='Products')

    def action_print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'product_ids': self.product_ids.ids,
            },
        }
        return self.env.ref('stock_analysis_report.action_stock_analysis_report').report_action(self, data=data)
