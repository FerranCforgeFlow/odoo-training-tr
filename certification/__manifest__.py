# Copyright 2014-2015 Grupo ESOC <www.grupoesoc.es>
# Copyright 2017-Apertoso N.V. (<http://www.apertoso.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Certification",
    "summary": "Defines  certification for different purposes",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "12.0.1.0.0",
    "category": "Certification Management",
    "website": "https://github.com/OCA/partner-contact",
    "license": "AGPL-3",
    'depends': ['base'],
    "data": ["security/ir.model.access.csv","security/certification_security.xml","views/certification.xml","views/certification_standard.xml","views/res_partner.xml","views/certification_bodies.xml","data/certification_data.xml"],
}
