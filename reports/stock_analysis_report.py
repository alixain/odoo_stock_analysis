# Path: /etc/odoo/addons/stock_analysis_report/reports/stock_analysis_report.py

from odoo import api, models
from datetime import datetime

class StockAnalysisReport(models.AbstractModel):
    _name = 'report.stock_analysis_report.stock_analysis_report_template'
    _description = 'Stock Analysis Report'

    def _get_starting_balance(self, product, start_date):
        # Get initial stock from quants
        quants = self.env['stock.quant'].search([
            ('product_id', '=', product.id),
            ('location_id.usage', '=', 'internal')
        ])
        current_qty = sum(quants.mapped('quantity'))

        # Calculate all moves after start_date to subtract from current quantity
        moves_after = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('date', '>=', start_date),
            ('state', '=', 'done'),
        ])

        # Reverse calculate the quantity at start date
        for move in moves_after:
            if move.location_dest_id.usage == 'internal' and move.location_id.usage != 'internal':
                current_qty -= move.product_qty
            elif move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal':
                current_qty += move.product_qty

        return current_qty

    def _get_move_quantities(self, product, start_date, end_date):
        moves = self.env['stock.move'].search([
            ('product_id', '=', product.id),
            ('date', '>=', start_date),
            ('date', '<=', end_date),
            ('state', '=', 'done'),
        ])

        in_qty = sum(moves.filtered(
            lambda m: m.location_dest_id.usage == 'internal' and 
                     m.location_id.usage != 'internal'
        ).mapped('product_qty'))

        out_qty = sum(moves.filtered(
            lambda m: m.location_id.usage == 'internal' and 
                     m.location_dest_id.usage != 'internal'
        ).mapped('product_qty'))

        return in_qty, out_qty

    def _is_below_min_stock(self, product, end_balance):
        # Get min stock value from product template
        min_stock = product.product_tmpl_id.x_min_low_stock_alert
        # Check if min stock is defined and end balance is below or equal to it
        if min_stock and end_balance <= min_stock:
            return True
        return False

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        product_ids = data['form']['product_ids']
        include_tag_ids = data['form']['include_tag_ids']
        exclude_tag_ids = data['form']['exclude_tag_ids']
        filter_by_tags = data['form']['filter_by_tags']

        # Get all stockable products first
        domain = [('type', '=', 'product')]
        
        # Filter by specific products if provided
        if product_ids and not filter_by_tags:
            domain.append(('id', 'in', product_ids))
        
        products = self.env['product.product'].search(domain)
        
        # Apply tag filtering if enabled
        if filter_by_tags:
            filtered_products = self.env['product.product']
            
            # Check if we're accessing tags using product_tag_ids field
            tag_field = 'product_tag_ids'
            
            for product in products:
                # Get product tags
                product_tags = product.product_tmpl_id[tag_field].ids
                
                # Skip products with excluded tags
                if exclude_tag_ids and any(tag_id in product_tags for tag_id in exclude_tag_ids):
                    continue
                
                # Include products with specified tags
                if include_tag_ids:
                    if any(tag_id in product_tags for tag_id in include_tag_ids):
                        filtered_products |= product
                else:
                    # If no include tags specified, include all products that don't have excluded tags
                    filtered_products |= product
            
            products = filtered_products
        
        report_data = []
        for product in products:
            # Get starting balance
            start_balance = self._get_starting_balance(product, start_date)
            
            # Get in/out quantities
            in_qty, out_qty = self._get_move_quantities(product, start_date, end_date)
            
            # Calculate end balance
            end_balance = start_balance + in_qty - out_qty
            
            # Check if below min stock level
            is_below_min = self._is_below_min_stock(product, end_balance)
            
            # Get product tags for display
            product_tags = product.product_tmpl_id.product_tag_ids
            
            report_data.append({
                'product': product,
                'start_balance': start_balance,
                'in_qty': in_qty,
                'out_qty': out_qty,
                'end_balance': end_balance,
                'min_stock': product.product_tmpl_id.x_min_low_stock_alert or 0,
                'is_below_min': is_below_min,
                'tags': product_tags,
            })

        # Get tag records for report header
        include_tags = self.env['product.tag'].browse(include_tag_ids) if include_tag_ids else []
        exclude_tags = self.env['product.tag'].browse(exclude_tag_ids) if exclude_tag_ids else []

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'data': data['form'],
            'report_data': report_data,
            'start_date': start_date,
            'end_date': end_date,
            'include_tags': include_tags,
            'exclude_tags': exclude_tags,
        }