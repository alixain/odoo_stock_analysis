{
    'name': 'Stock Analysis Report',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Generate detailed stock movement analysis reports',
    'description': """
        This module provides a detailed stock analysis report with:
        * Starting balance
        * Incoming movements
        * Outgoing movements
        * Ending balance
        * Filter by date range, products and product tags
    """,
    'depends': ['base', 'stock', 'product_tags'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_analysis_wizard_view.xml',
        'reports/stock_analysis_report.xml',
        'reports/stock_analysis_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}