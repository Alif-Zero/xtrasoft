from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class loanRequestForm(models.Model):
    _name = 'loan.request.form'

    name = fields.Char(string="Name ")
    employee_detail = fields.Char(string="Employee Detail ")
    employee_code = fields.Char(string="Employee Code ")
    employee_designation = fields.Char(string="Employee Designation ")
    department_name = fields.Char(string="Department Name")
    employee_date = fields.Date(string="Date")
    employee_cnic = fields.Char(string="CNIC#")
    employee_salary = fields.Integer(string="Employee Salary")
    last_loan_amount = fields.Integer(string="Last Loan Amount")
    current_loan_balance = fields.Integer(string="Current Loan")
    required_loan_amount = fields.Integer(string="Required Loan Amount")
    approved_loan_amount = fields.Integer(string="Approved Loan Amount")

    father_name = fields.Char(string="Father Name ")
    father_occupation = fields.Char(string="Father Occupation ")
    father_cnic = fields.Char(string="Father CNIC ")
    father_address = fields.Char(string="Address ")
    reason_of_loan = fields.Text(string="Reason For Taking Loan ")


    monthly_deduction_amount = fields.Char(string="Monthly Deduction Amount ")


    g_1_name = fields.Char(string="Name")
    g_1_department = fields.Char(string="Department")
    g_1_designation = fields.Char(string="Designation")
    g_1_contact_no = fields.Char(string="Contact No")
    g_1_cnic = fields.Char(string="CNIC")
    g_1_address = fields.Text(string="Address")



    g_2_name = fields.Char(string="Name")
    g_2_department = fields.Char(string="Department")
    g_2_designation = fields.Char(string="Designation")
    g_2_contact_no = fields.Char(string="Contact No")
    g_2_cnic = fields.Char(string="CNIC")
    g_2_address = fields.Text(string="Address")








