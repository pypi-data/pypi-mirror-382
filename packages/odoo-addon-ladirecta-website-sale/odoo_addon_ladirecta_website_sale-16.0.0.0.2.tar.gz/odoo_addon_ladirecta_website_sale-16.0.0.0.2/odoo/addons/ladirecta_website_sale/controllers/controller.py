from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteContactSale(WebsiteSale):
    def _get_mandatory_fields_billing(self, country_id=False):
        return [
            fname
            for fname in super(WebsiteContactSale, self)._get_mandatory_fields_billing(
                country_id
            )
            if fname != "name"
        ]

    def _get_mandatory_fields_shipping(self, country_id=False):
        return [
            fname
            for fname in super(WebsiteContactSale, self)._get_mandatory_fields_shipping(
                country_id
            )
            if fname != "name"
        ]
