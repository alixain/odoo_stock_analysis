from odoo import api, fields, models
from datetime import datetime

class StockAnalysisWizard(models.TransientModel):
    _name = 'stock.analysis.wizard'
    _description = 'Stock Analysis Report Wizard'

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', required=True, default=fields.Date.context_today)
    product_ids = fields.Many2many('product.product', string='Products')
    include_tag_ids = fields.Many2many('product.tag', string='Include Tags', 
                                       relation='stock_analysis_include_tag_rel',
                                       help="Only include products with these tags")
    exclude_tag_ids = fields.Many2many('product.tag', string='Exclude Tags', 
                                       relation='stock_analysis_exclude_tag_rel',
                                       help="Exclude products with these tags")
    filter_by_tags = fields.Boolean(string='Filter by Tags', default=False)

    @api.onchange('filter_by_tags')
    def _onchange_filter_by_tags(self):
        # Clear product selection when switching to tag filtering
        if self.filter_by_tags:
            self.product_ids = [(5, 0, 0)]  # Clear the many2many field

    def action_print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'product_ids': self.product_ids.ids,
                'include_tag_ids': self.include_tag_ids.ids,
                'exclude_tag_ids': self.exclude_tag_ids.ids,
                'filter_by_tags': self.filter_by_tags,
            },
        }
        return self.env.ref('stock_analysis_report.action_stock_analysis_report').report_action(self, data=data)