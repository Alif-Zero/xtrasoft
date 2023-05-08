import time

from odoo import models, fields, api, _
from calendar import isleap
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class HrEmployeeDetails(models.Model):
    _name='hr.education.details'
    employee_id=fields.Many2one('hr.employee')
    name=fields.Char('Degree Name',required=True)
    type=fields.Char('Degree Type',required=True)
    degree_level=fields.Selection([('graduate','Graduate'),('bachelor','Bachelor'),('master','Master'),('doctor','Doctor'),('other','Other')],'Certificate Level',required=True)
    institute_id=fields.Many2one('hr.institute','Institute',required=True)

class HrInstitute(models.Model):
    _name='hr.institute'
    name=fields.Char('Institute',required=True)

class HrEmployementHistory(models.Model):
    _name='hr.employeement.history'
    employee_id=fields.Many2one('hr.employee')
    institute_id=fields.Many2one('hr.institute','Company Name',required=True)
    designation_id=fields.Many2one('hr.job','Last Designation',required=True)
    department=fields.Char('Department',required=True)
    from_date=fields.Date('From Date',required=True)
    to_date=fields.Date('To Date',required=True)
    leaving_reason=fields.Text('Reason for Leaving',required=True)
    
class inherithremploye(models.Model):
    _inherit = 'hr.employee'

    bahrain_expact = fields.Selection([('Bahraini', 'Bahraini'), ('Expats', 'Expats')], string='Bahranis/Expacts', )
    muslim = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Muslim', )
    age = fields.Char(string="Age", compute='set_age_computed')
    no_depend = fields.Integer(string='Dependant#')
    cpr_no = fields.Char(string="CNIC")
    cpr_exp_date = fields.Date(string="CNIC Expiry")
    passport_exp_date = fields.Date(string="Passport Expiry")
#     rp_exp_date = fields.Date(string="RP Expiry")
    veh_alloted = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string='Vehicle Alloted')
    veh_number = fields.Char(string="Vehicle#", help="Vehicle Number")
    accomodation = fields.Selection([('YES', 'YES'), ('NO', 'NO')], string='Acomodation')

    ot_eligible = fields.Boolean(string="OT Eligible?", default=False)
    ot_weekday = fields.Boolean(string="OT Weekdays")
    ot_weekend = fields.Boolean(string="OT Weekends")

    ot_ramzan = fields.Boolean(string="OT Ramadan?")
    ot_ramzan_muslims = fields.Boolean(string="OT Ramadan muslims only?")

    sat_work = fields.Boolean(string="Saturday Workers?", default=True)
    sat_offic = fields.Boolean(string="Saturday officers?")

    manual_schedule = fields.Boolean(string="Manual schedule?")

    workschedule = fields.Selection(
        [('08:00-13:00|14:00-17:00', '08:00-13:00|14:00-17:00'), ('08:30-13:00|14:30-18:00', '08:30-13:00|14:30-18:00'),
         ('08:30|15:00', '08:30|15:00')],
        string="Select schedule")

    man_works_fhour = fields.Char("First shift start")
    man_works_fmins = fields.Char("First shift end")

    man_works_shour = fields.Char("Second shift start")
    man_works_smins = fields.Char("second shift end")
    iban = fields.Char(string="IBAN")
    emergency_person_relation=fields.Char('Contact Relation')
    education_details=fields.One2many('hr.education.details','employee_id','Education Details')
    experience_history=fields.One2many('hr.employeement.history','employee_id','Employement History')
    
    @api.onchange('man_works_fhour', 'man_works_fmins', 'man_works_shour', 'man_works_smins')
    def onchangmanul_work(self):
        if self.man_works_fhour:
            try:
                time_obj_first_check_out = fields.datetime.strptime(self.man_works_fhour, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_fmins:
            try:
                time_obj_first_check_out = fields.datetime.strptime(self.man_works_fmins, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_shour:
            try:
                time_obj_first_check_out = fields.datetime.strptime(self.man_works_shour, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))
        if self.man_works_smins:
            try:
                time_obj_first_check_out = fields.datetime.strptime(self.man_works_smins, '%H:%M')
            except:
                raise ValidationError(_("Follow Correct Format 00:00"))

    @api.onchange('workschedule')
    def onchangeschedule_work(self):
        if self.workschedule:
            if self.workschedule == '08:30|03:00' and self.ot_ramzan:
                pass
            elif self.ot_ramzan:
                raise UserError('Wrong schedule seclected')

    @api.onchange('ot_ramzan_muslims')
    def onchanotrmza_work(self):
        if self.ot_ramzan_muslims:
            if self.muslim:
                pass
            else:
                raise UserError('Cannot apply on Non-Muslim')

    @api.onchange('ot_ramzan')
    def oncrnana_work(self):
        if self.ot_ramzan:
            self.manual_schedule = False
            self.workschedule = '08:30|03:00'

    def calculateAge(self, dob):
        today = date.today()
        try:
            birthday = dob.replace(year=today.year)

            # raised when birth date is February 29
        # and the current year is not a leap year
        except ValueError:
            birthday = dob.replace(year=today.year,
                                   month=dob.month + 1, day=1)

        if birthday > today:
            return today.year - dob.year - 1
        else:
            return today.year - dob.year

    def set_age_computed(self):
        if self.birthday:
            self.age = str(self.calculateAge(self.birthday))
        else:
            self.age = "N/A"

    # designation=fields.Many2one('employee.designation',)


class inheritcontracts(models.Model):
    _inherit = 'hr.contract'
    
    on_probation=fields.Boolean('On Probation')
    probation_duration=fields.Integer('Probation Duration (In Months)')
    notice_period=fields.Integer('Notice Period  (In Months)')
    confirmation_due_date=fields.Date('Confirmation Due Date')
    extend_notice_period=fields.Boolean('Extend Probation')
    extension_duration=fields.Integer('Extension (In Days)')
    utility=fields.Float('Utility', default=0.00,compute="_cal_allowances")
    fuel_allowance=fields.Float('Fuel Allowance', default=0.00)
    housing_allowance = fields.Float("House Rent", default=0.00,compute="_cal_allowances")
    travel_allowance = fields.Float("Travel Allowance", default=0.00)
    
    increment_Date = fields.Date(string="Increment Date")
    increment_Amount = fields.Float("Amount", default=0.00)
    wage = fields.Monetary('Basic', required=True, tracking=True, help="Employee's monthly gross wage.",compute="_cal_allowances")
    leave_Status = fields.Selection(
        [('Active', 'Active'), ('Terminated', 'Terminated'), ('Resigned', 'Resigned'), ('Vacation', 'Vacation')],
        string='Leave Status', )
    leave_due = fields.Float("Leave Due", default=0.00)
    leave_amount = fields.Float("Leave Amount", default=0.00)
    total_work_experience = fields.Char(string="Total Work Experience")
    indemnity = fields.Char(string="Indemnity")
    tenure = fields.Char(string="Tenure")
    sponsorship = fields.Selection([('Design Creative', 'Design Creative'), ('Design Grafix', 'Design Grafix')],
                                   string='Sponsorship', )
    work_location = fields.Selection([('DG', 'DG'), ('DC', 'DC')], string='Work Location', )
    gosi_Salary_Deduction = fields.Float("GOSI Salery deduction", default=0.00)
    hourly_salery = fields.Float("Hourly salery", default=0.00)
    Misce_Allowance = fields.Float("Miscellaneous Allowance", default=0.00)
    OT = fields.Float("OT", default=0.00)
    OT1 = fields.Float("OT 1", default=0.00)
    OT2 = fields.Float("OT 2", default=0.00)
    OTw = fields.Float("OT(W)", default=0.00)

    p_salery = fields.Monetary(string="Salary")
    p_salery_pd = fields.Monetary(string='Salary / Day', digits=(16, 3), default=0.0, compute='salery_comp', store=True)
    p_salery_ph = fields.Monetary(string='Salary / Hour', digits=(16, 3), default=0.0, compute='salery_comp',
                                  store=True)

    department_id = fields.Many2one(related='employee_id.department_id', string="Department")

    # p_leave_salery=fields.Monetary(string='Leave Salary',digits=(16, 3))
    p_leave_salery_pd = fields.Monetary(string='Leave Salary / Day', digits=(16, 3), default=0.0, )
    p_leave_salery_ph = fields.Monetary(string='Leave Salary /  Hour', digits=(16, 3), default=0.0, )

    # p_ideminity=fields.Monetary(string='Ideminity',digits=(16, 3))
    p_ideminity_pd = fields.Monetary(string='Ideminity / Day', digits=(16, 4), default=0.0)
    p_ideminity_ph = fields.Monetary(string='Ideminity / hour', digits=(16, 4), default=0.0)

    p_airfair = fields.Monetary(string='Airfare', digits=(16, 3))
    p_airfair_pd = fields.Monetary(string='Airfare / Day', digits=(16, 3), default=0.0, store=True, compute='air_comp')
    p_airfair_ph = fields.Monetary(string='Airfare / hour', digits=(16, 3), default=0.0, store=True, compute='air_comp')

    p_lmra = fields.Monetary(string='Lmra', digits=(16, 3))
    p_lmra_pd = fields.Monetary(string='Lmra / Day', digits=(16, 3), default=0.0, store=True, compute='lmra_comp')
    p_lmra_ph = fields.Monetary(string='Lmra / Hour', digits=(16, 3), default=0.0, store=True, compute='lmra_comp')

    p_visa = fields.Monetary(string='Visa', digits=(16, 3))
    p_visa_pd = fields.Monetary(string='Visa / Day', digits=(16, 3), default=0.0, store=True, compute='visa_comp')
    p_visa_ph = fields.Monetary(string='Visa / hour', digits=(16, 3), default=0.0, store=True, compute='visa_comp')

    p_gosi_pd = fields.Monetary(string='Gosi / Day', digits=(16, 3), default=0.0)
    p_gosi_ph = fields.Monetary(string='Gosi / Hour', digits=(16, 3), default=0.0)
    grade = fields.Many2one('hr.grade', string="Grade")
    final_hourly_rate = fields.Monetary('Final  / hourly rate', compute='get_hourly_final')
    final_day_rate = fields.Monetary('Final / Day rate', compute='get_hourly_final')

    gosi_salery = fields.Monetary(string='Gosi Salery', digits=(16, 3), default=0.0)
#     gross_salery = fields.Monetary(string='Gross Salery', digits=(16, 3), compute='get_gross_salery')
    gross_salery = fields.Monetary(string='Gross Salery', digits=(16, 3))
    select_incrmnt = fields.Selection([('Basic', 'Basic'), ('Housing', 'Housing'), ('Travel', 'Travel')],
                                      string='Increment Type')
    select_decrement = fields.Selection([('Basic', 'Basic'), ('Housing', 'Housing'), ('Travel', 'Travel')],
                                        string='Decrement Type')
    do_incrmnt = fields.Boolean('Will Increment?', default=False)
    do_decre = fields.Boolean('Will Decrement?', default=False)
    
    
    
    @api.depends('gross_salery','fuel_allowance')
    def _cal_allowances(self):
        for each in self:
            if each.gross_salery and each.fuel_allowance:
                each.utility=((each.gross_salery+each.fuel_allowance)*20)/100
                each.housing_allowance=((each.gross_salery+each.fuel_allowance)*30)/100
                each.wage=((each.gross_salery+each.fuel_allowance)*20)/100
            elif each.gross_salery:
                each.utility=(each.gross_salery*20)/100
                each.housing_allowance=(each.gross_salery*30)/100
                each.wage=(each.gross_salery*50)/100
            else:
                each.utility=0.0
                each.housing_allowance=0.0
                each.wage=0.0
                
    @api.onchange('extend_notice_period','extension_duration')
    def cal_notice_end_date(self):
        if self.extension_duration and self.extend_notice_period and self.date_end:
            end_date=datetime.strptime(str(self.date_end), '%Y-%m-%d')
            self.date_end = end_date + relativedelta(days=self.extension_duration)
            
    @api.onchange('on_probation','probation_duration')
    def cal_end_date(self):
        if self.on_probation and self.probation_duration and self.date_start:
            start_date=datetime.strptime(str(self.date_start), '%Y-%m-%d')
            self.date_end = start_date + relativedelta(months=self.probation_duration)
            self.confirmation_due_date=start_date + relativedelta(months=self.probation_duration) - relativedelta(days=1)
            
    @api.onchange('grade')
    def onchange_departmentgrx(self):
        if self.grade:
            self.employee_id.department_id = self.grade.department.id
            self.employee_id.job_id = self.grade.designation.id
            self.employee_id.job_title = self.grade.designation.name

    @api.onchange('increment_Amount')
    def onchange_select_incrmnt(self):
        if self.do_incrmnt:
            if self.select_incrmnt == 'Basic':
                self.wage += self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_incrmnt == 'None':
                pass
            elif self.select_incrmnt == 'Housing':
                self.housing_allowance += self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_incrmnt == 'Travel':
                self.travel_allowance += self.increment_Amount
                self.increment_Amount = 0.0
        elif self.do_decre:
            if self.select_decrement == 'Basic':
                self.wage -= self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_decrement == 'Housing':
                self.housing_allowance -= self.increment_Amount
                self.increment_Amount = 0.0
            elif self.select_decrement == 'Travel':
                self.travel_allowance -= self.increment_Amount
                self.increment_Amount = 0.0

    @api.onchange('gosi_salery')
    def onchange_gosisalery(self):
        if self.gosi_salery:
            if self.employee_id.bahrain_expact == 'Bahraini':
                self.gosi_Salary_Deduction = (self.gosi_salery * 7) / 100
            else:
                self.gosi_Salary_Deduction = (self.gosi_salery * 1) / 100

    @api.depends('wage', 'housing_allowance', 'travel_allowance', 'increment_Amount', 'gosi_Salary_Deduction')
    def get_gross_salery(self):
        for rec in self:
            rec.gross_salery = (
                                       rec.wage + rec.housing_allowance + rec.travel_allowance + rec.increment_Amount) - rec.gosi_Salary_Deduction

    @api.depends('p_salery', 'p_airfair', 'p_lmra', 'p_visa')
    def get_hourly_final(self):
        for rec in self:
            rec.final_hourly_rate = rec.p_salery_ph + rec.p_leave_salery_ph + rec.p_airfair_ph + rec.p_ideminity_ph + rec.p_lmra_ph + rec.p_visa_ph \
                                    + rec.p_gosi_ph
            rec.final_day_rate = rec.p_salery_pd + rec.p_leave_salery_pd + rec.p_airfair_pd + rec.p_ideminity_pd + rec.p_lmra_pd + rec.p_visa_pd \
                                 + rec.p_gosi_pd

    @api.depends('p_salery')
    def salery_comp(self):
        for rec in self:
            if rec.p_salery:
                # leave calcualtion
                year = fields.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_leave_salery_pd = rec.p_salery / 366
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

                    rec.p_ideminity_pd = rec.p_salery / 366
                    rec.p_ideminity_ph = rec.p_ideminity_pd / 8
                else:
                    rec.p_leave_salery_pd = rec.p_salery / 365
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

                    rec.p_ideminity_pd = rec.p_salery / 365
                    rec.p_ideminity_ph = rec.p_ideminity_pd / 8

                # salery calculation
                rec.p_salery_pd = rec.p_salery / 30
                rec.p_salery_ph = rec.p_salery_pd / 8
                # Gosi calculation
                citizen = rec.employee_id.bahrain_expact

                if citizen == 'Expats':
                    rec.p_gosi_pd = ((rec.p_salery * 3) / 100) / 30
                    rec.p_gosi_ph = rec.p_gosi_pd / 8

                elif citizen == 'Bahraini':
                    rec.p_gosi_pd = ((rec.p_salery * 12) / 100) / 30
                    rec.p_gosi_ph = rec.p_gosi_pd / 8
                # indiminity calculation

    @api.depends('p_leave_salery')
    def leave_comp(self):
        for rec in self:
            if rec.p_leave_salery:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_leave_salery_pd = rec.p_leave_salery / 366
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8
                else:
                    rec.p_leave_salery_pd = rec.p_leave_salery / 365
                    rec.p_leave_salery_ph = rec.p_leave_salery_pd / 8

    @api.depends('p_airfair')
    def air_comp(self):
        for rec in self:
            if rec.p_airfair:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = fields.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_airfair_pd = rec.p_airfair / 731
                    rec.p_airfair_ph = rec.p_airfair_pd / 8
                else:
                    rec.p_airfair_pd = rec.p_airfair / 730
                    rec.p_airfair_ph = rec.p_airfair_pd / 8

    # @api.depends('p_ideminity')
    # def ideminity_comp(self):
    #     for rec in self:
    #         if rec.p_ideminity:
    #             # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))
    #
    #             year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')
    #
    #             # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
    #             if isleap(int(year)):
    #                 rec.p_ideminity_pd = rec.p_ideminity / 366
    #                 rec.p_ideminity_ph = rec.p_ideminity_pd / 8
    #             else:
    #                 rec.p_ideminity_pd = rec.p_ideminity / 365
    #                 rec.p_ideminity_ph = rec.p_ideminity_pd / 8

    @api.depends('p_lmra')
    def lmra_comp(self):
        for rec in self:
            if rec.p_lmra:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                # year = datetime.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                rec.p_lmra_pd = rec.p_lmra / 30
                rec.p_lmra_ph = rec.p_lmra_pd / 8

    @api.depends('p_visa')
    def visa_comp(self):
        for rec in self:
            if rec.p_visa:
                # year = time.strftime('%Y', time.strptime(str(fields.Datetime.now().date().year), "%Y"))

                year = fields.datetime.strptime(str(fields.Datetime.now().date()), "%Y-%m-%d").strftime('%Y')

                # year = datetime.datetime.strptime(fields.Datetime.now().strftime("%Y"))
                if isleap(int(year)):
                    rec.p_visa_pd = rec.p_visa / 731
                    rec.p_visa_ph = rec.p_visa_pd / 8
                else:
                    rec.p_visa_pd = rec.p_visa / 730
                    rec.p_visa_ph = rec.p_visa_pd / 8




    def get_latein_amount(self, employee_id, basic_salary, from_date, to_date):
        # so get attendance between those date
        # apply_latein_deduction and exception_approved, count the numbers and if yes then get then divide it by 2, so you have to deduct this day salary
        # get basic salary half day calulcations so its ok get it by multiply

        attendance_days_count = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date),
             ('attendance_date', '<=', to_date), ('exception_approved', '=', False),
             ('apply_latein_deduction', '=', True)])
        if attendance_days_count:
            t_hours=0.0
            t_mins=0.0
            for rec in attendance_days_count:
                if rec.late_in:
                    hrs,mins=int(rec.late_in.split(':')[0]),int(rec.late_in.split(':')[1])
                    t_hours+=hrs
                    t_mins+=mins
            t_hours+=t_mins/60
            # num_days_deducted = attendance_days_count / 2
            return t_hours
        else:
            return 0

    def get_perminute_rate(self, basic_salary):
        perday = basic_salary / 30
        working_hours = perday / 8
        perminute = working_hours / 60
        return perminute

    def get_ot_125(self, employee_id, basic_salary, from_date, to_date):
        attendance_rec = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date), ('allow_viewoto', '=', True),
             ('attendance_date', '<=', to_date), ('ot_125', '!=', None)])
        attendance_rec_minutes = 0
        if attendance_rec:
            print(attendance_rec[0])
            for rec in range(len(attendance_rec)):
                attendance_rec_minutes += int(attendance_rec[rec].ot_125.split(':')[0]) * 60 + int(
                    attendance_rec[rec].ot_125.split(':')[1])
            # inke minuts ko sum kr ke perminute rate * 1.25
            perminute = self.get_perminute_rate(basic_salary)
            return attendance_rec_minutes * 1.25 * perminute
        else:
            return 0

    def get_ot_15(self, employee_id, basic_salary, from_date, to_date):
        attendance_rec = self.env['attendance.custom'].search(
            [('employee_id', '=', employee_id), ('attendance_date', '>=', from_date), ('allow_viewotf', '=', True),
             ('attendance_date', '<=', to_date), ('ot_125', '!=', None)])
        attendance_rec_minutes = 0
        if attendance_rec:
            print(attendance_rec[0])
            for rec in range(len(attendance_rec)):
                attendance_rec_minutes += int(attendance_rec[rec].ot_15.split(':')[0]) * 60 + int(
                    attendance_rec[rec].ot_15.split(':')[1])
            # inke minuts ko sum kr ke perminute rate * 1.25
            perminute = self.get_perminute_rate(basic_salary)
            return attendance_rec_minutes * 1.50 * perminute
        else:
            return 0

    def get_basic_salery(self,wage,days):
        result=(((wage)*12)/365)*(days)
        return result

    def get_housing_allow(self,allow,days):
        result = (((allow) * 12) / 365) * (days)
        return result

    def get_travel_allow(self,allow,days):
        result = (((allow) * 12) / 365) * (days)
        return result


    def get_absent_deduc(self,days):

        return days


class accacc_mov(models.Model):
    _inherit = 'account.account'

    def _set_opening_debit_credit(self, amount, field):
        """ Generic function called by both opening_debit and opening_credit's
        inverse function. 'Amount' parameter is the value to be set, and field
        either 'debit' or 'credit', depending on which one of these two fields
        got assigned.
        """
        opening_move = self.company_id.account_opening_move_id

        if not opening_move:
            raise UserError(_("You must first define an opening move."))

        if opening_move.state == 'draft':
            # check whether we should create a new move line or modify an existing one
            opening_move_line = self.env['account.move.line'].search([('account_id', '=', self.id),
                                                                      ('move_id', '=', opening_move.id),
                                                                      (field, '!=', False),
                                                                      (field, '!=',
                                                                       0.0)])  # 0.0 condition important for import

            counter_part_map = {'debit': opening_move_line.credit, 'credit': opening_move_line.debit}
            # No typo here! We want the credit value when treating debit and debit value when treating credit

            if opening_move_line:
                if amount:
                    # modify the line
                    opening_move_line.with_context(check_move_validity=False)[field] = amount
                elif counter_part_map[field]:
                    # delete the line (no need to keep a line with value = 0)
                    opening_move_line.with_context(check_move_validity=False).unlink()
            elif amount:
                # create a new line, as none existed before
                self.env['account.move.line'].with_context(check_move_validity=False).create({
                    'name': _('Opening balance'),
                    field: amount,
                    'move_id': opening_move.id,
                    'account_id': self.id,
                })

            # Then, we automatically balance the opening move, to make sure it stays valid
            if not 'import_file' in self.env.context:
                # When importing a file, avoid recomputing the opening move for each account and do it at the end, for better performances
                self.company_id._auto_balance_opening_move()


class hr_gradeclass(models.Model):
    _name = 'hr.grade'
    _rec_name = 'name'

    name = fields.Char(string="Name", compute='comp_name', store=True)
    grade = fields.Char(string="Grade", required=1)
    department = fields.Many2one('hr.department', string='Department', required=1)
    designation = fields.Many2one('hr.job', string='Grade Level', required=1)

    @api.onchange('department')
    def onchange_department(self):
        self.designation = None

    @api.constrains('department')
    def change_department(self):
        if self.department:
            self.designation.department_id = self.department.id
            get_contr = self.env['hr.contract'].search([('grade', '=', self.id)], limit=1)
            if get_contr:
                get_contr.employee_id.department_id = self.department.id
                get_contr.employee_id.job_id = self.designation.id

    @api.constrains('designation')
    def chng_designamtion(self):
        if self.designation:
            get_contr = self.env['hr.contract'].search([('grade', '=', self.id)], limit=1)
            if get_contr:
                get_contr.employee_id.job_title = self.designation.name
                get_contr.employee_id.job_id = self.designation.id

    @api.depends('grade', 'department', 'designation')
    def comp_name(self):
        for rec in self:
            if rec.grade and rec.department and rec.designation:
                rec.name = rec.grade + '-' + rec.designation.name + '-' + rec.department.name

    # @api.constrains('grade','department','designation')
    # def _check_name(self):
    #     for rec in self:
    #         record_exist = self.env['hr.grade'].search([('grade', '=', rec.grade),('department', '=', rec.department.id),('designation', '=', rec.designation.id)])
    #         if len(record_exist) > 1:
    #             raise UserError('Grade for selected department and designation already exist')
