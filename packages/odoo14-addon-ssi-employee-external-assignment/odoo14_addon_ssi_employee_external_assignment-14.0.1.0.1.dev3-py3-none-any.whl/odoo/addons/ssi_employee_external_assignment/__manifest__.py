# Copyright 2025 OpenSynergy Indonesia
# Copyright 2025 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Employee External Assignment",
    "version": "14.0.1.0.0",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "website": "https://github.com/open-synergy/employee-external-assignment",
    "license": "AGPL-3",
    "depends": [
        "ssi_master_data_mixin",
        "ssi_transaction_confirm_mixin",
        "ssi_transaction_open_mixin",
        "ssi_transaction_done_mixin",
        "ssi_transaction_cancel_mixin",
        "ssi_transaction_terminate_mixin",
        "ssi_employee_document_mixin",
        "ssi_transaction_date_duration_mixin",
    ],
    "data": [
        "security/ir_module_category/employee_external_assignment_module_category.xml",
        "security/res_groups/employee_external_assignment_type.xml",
        "security/res_groups/employee_external_assignment.xml",
        "security/ir_model_access/employee_external_assignment_type.xml",
        "security/ir_model_access/employee_external_assignment.xml",
        "security/ir_rule/employee_external_assignment.xml",
        "ir_sequence/employee_external_assignment.xml",
        "sequence_template/employee_external_assignment.xml",
        "policy_template/employee_external_assignment.xml",
        "approval_template/employee_external_assignment.xml",
        "views/employee_external_assignment_type_views.xml",
        "views/employee_external_assignment_views.xml",
        "views/hr_employee.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
