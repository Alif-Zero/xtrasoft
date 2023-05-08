from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class inherithremploye(models.Model):
    _inherit = 'product.template'


    name = fields.Char('Name', index=True, translate=True,default="-")

    model = fields.Char("Model")
    Material=fields.Char("Material")
    description=fields.Char("description")
    sequence=fields.Integer()


    p_type=fields.Many2one('product.type',string="Type")
    p_color=fields.Many2one('product.color',string="Color")

    p_length=fields.Many2one('product.length',string="Length")

    p_width=fields.Many2one('product.width',string="Width")
    p_height=fields.Many2one('product.height',string="Height")
    p_made=fields.Many2one('product.made',string="Made")

    p_size=fields.Char(string="Size")

    brand= fields.Many2one('brand', string='Brand')
    raw_mat = fields.Boolean(string="Raw Material", default=False)
    final_prod = fields.Boolean(string="Final Product", default=False)
    overhead_mat = fields.Boolean(string="Overhead Materail", default=False)


    p_watt=fields.Many2one('product.watt',string="Watt")
    p_model=fields.Many2one('product.model',string="Model")

    p_ip=fields.Many2one('product.ip',string="IP")

    p_shape=fields.Many2one('product.shape',string="Shape")
    p_shade=fields.Many2one('product.shade',string="Shade")
    p_srno=fields.Many2one('product.srno',string="Sr.No")

    Tickness=fields.Char(string="Thickness")

    Total_sq_meter=fields.Float(string="Total sq meter")
    Rate_per_SqMtr = fields.Float(string="Rate/sq meter")
    running_meter_cost = fields.Float(string="running meter cost")





    # def calc_meters_value(self):
    #     for rec in self:


    @api.constrains('p_length','p_width','standard_price')
    def calc_sqmrmc(self):
        if self.p_length and self.p_width:
            if self.p_length.name and self.p_width.name:
                cal_len = float(''.join(x for x in self.p_length.name if x.isdigit()))
                cal_width = float(''.join(x for x in self.p_width.name if x.isdigit()))
                if cal_width and cal_len:
                    self.Total_sq_meter = cal_len * cal_width
                    self.Rate_per_SqMtr = self.standard_price / self.Total_sq_meter
                else:
                    self.Total_sq_meter = 0.0
                    self.Rate_per_SqMtr = 0.0

                if cal_len and self.standard_price > 0:

                   self.running_meter_cost = self.standard_price / cal_len
                else:
                   self.running_meter_cost = 0.0
            else:
                   self.Total_sq_meter = 0.0
                   self.running_meter_cost = 0.0
                   self.Rate_per_SqMtr = 0.0
        else:
           self.Total_sq_meter = 0.0
           self.running_meter_cost = 0.0
           self.Rate_per_SqMtr = 0.0



    @api.constrains('raw_mat','p_length','categ_id','p_width','p_height','p_color','p_type','p_made','brand')
    def check_write(self):
        if self.raw_mat or self.overhead_mat:
            if self.categ_id.parent_id:
                names = self.categ_id.parent_id.name + ' ' + self.categ_id.name + ' '
            else:
                names = self.categ_id.name + ' '
            if self.p_length:
                names += self.p_length.name + ' '
            if self.p_width:
                names += 'X' + self.p_width.name + ' '
            if self.p_height:
                names += 'X' + self.p_height.name + ' '

            if self.p_color:
                names += self.p_color.name + ' '
            if self.p_type:
                names += self.p_type.name + ' '
            if self.p_made:
                names += self.p_made.name + ' '
            if self.brand:
                names += self.brand.name + ' '

            self.name=names

    # @api.model
    # def create(self, vals):
    #     res = super(inherithremploye, self).create(vals)
    #     if res.raw_mat:
    #         res.name=""
    #         if res.categ_id.parent_id:
    #            names=res.categ_id.parent_id.name + ' ' + res.categ_id.name + ' '
    #         else:
    #             names = res.categ_id.name + ' '
    #
    #         if res.p_length:
    #             names += res.p_length.name+' '
    #         if res.p_width:
    #             names += 'X' + res.p_width.name+' '
    #         if res.p_height:
    #             names += 'X' + res.p_height.name +' '
    #
    #
    #         if res.p_color:
    #             names += res.p_color.name+' '
    #         if res.p_type:
    #             names +=  res.p_type.name+' '
    #         if res.p_made:
    #             names +=  res.p_made.name +' '
    #         if res.brand:
    #             names += res.brand.name + ' '
    #
    #         # names+= res.p_color.name+' ' + res.p_type.name  + ' ' + res.p_made.name + ' ' + res.brand.name
    #         res.name=str(names)
    #
    #     return res
    #
    # def write(self, vals):
    #     if 'raw_mat' in vals:
    #         if vals['raw_mat'] == True:
    #             if self.categ_id.parent_id:
    #                 names = self.categ_id.parent_id.name + ' ' + self.categ_id.name + ' '
    #             else:
    #                 names = self.categ_id.name + ' '
    #             if self.p_length:
    #                names +=  self.p_length.name+' '
    #             if self.p_width:
    #                 names += 'X' + self.p_width.name+' '
    #             if self.p_height:
    #                 names += 'X' +self.p_height.name+' '
    #
    #             if self.p_color:
    #                 names += self.p_color.name + ' '
    #             if self.p_type:
    #                 names += self.p_type.name + ' '
    #             if self.p_made:
    #                 names += self.p_made.name + ' '
    #             if self.brand:
    #                 names += self.brand.name + ' '
    #
    #             # names+= self.p_color.name+' '+ self.p_type.name  + ' ' + self.p_made.name + ' ' + self.brand.name
    #             vals['name']=str(names)
    #     rslt = super(inherithremploye, self).write(vals)
    #     return rslt








class brandclas(models.Model):
    _name = 'brand'

    name=fields.Char("Brand")



class product_sizex(models.Model):
    _name = 'product.size'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")



class product_types(models.Model):
    _name = 'product.type'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")



class product_color(models.Model):
    _name = 'product.color'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")




class product_length(models.Model):
    _name = 'product.length'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")




class product_width(models.Model):
    _name = 'product.width'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")





class product_height(models.Model):
    _name = 'product.height'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")


class product_made(models.Model):
    _name = 'product.made'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")







class product_watt(models.Model):
    _name = 'product.watt'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

class product_model(models.Model):
    _name = 'product.model'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

class product_srno(models.Model):
    _name = 'product.srno'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

class product_shape(models.Model):
    _name = 'product.shape'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

class product_ip(models.Model):
    _name = 'product.ip'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

class product_shade(models.Model):
    _name = 'product.shade'

    name=fields.Char(string="name")
    desc=fields.Char(string="Description")

# class product_made(models.Model):
#     _name = 'product.type'
#
#     name=fields.Char(string="name")
#     desc=fields.Char(string="Description")




class emp_designation(models.Model):
    _name = 'employee.designation'
    _rec_name = 'designation'

    designation=fields.Char(string="Designation",required=1)
    rate=fields.Many2one('employee.rate',required=1)

class emp_designation_rate(models.Model):
    _name = 'employee.rate'
    _rec_name = 'rate'

    rate = fields.Float(string="Rate",required=1)
    desc = fields.Char(string="Description")







