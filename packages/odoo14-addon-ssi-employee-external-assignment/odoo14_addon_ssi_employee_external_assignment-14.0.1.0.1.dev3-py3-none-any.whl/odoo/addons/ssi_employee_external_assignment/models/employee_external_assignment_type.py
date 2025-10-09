# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class EmployeeExternalAssignmentType(models.Model):
    _name = "employee_external_assignment_type"
    _description = "Employee External Assignment Type"
    _inherit = ["mixin.master_data"]
