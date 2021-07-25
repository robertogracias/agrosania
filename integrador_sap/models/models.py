# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2017-2018 CodUP (<http://codup.com>).
#
##############################################################################
import base64
import json
import requests
import logging
from collections import OrderedDict
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class integrador_task(models.Model):
    _inherit='ir.cron'
    sap_task=fields.Boolean("Tarea de syncronizacion SAP")
    
class integrador_category(models.Model):
    _inherit='product.category'
    code=fields.Integer("Codigo")

class integrador_user(models.Model):
    _inherit='res.users'
    code=fields.Integer("Codigo")

class integrador_pricelist(models.Model):
    _inherit='product.pricelist'
    code=fields.Integer("Codigo")
    factor=fields.Float("Factor")
    
class integrador_location(models.Model):
    _inherit='stock.location'
    code=fields.Char("Codigo")

class integrador_property(models.Model):
    _name='integrador_sap.property'
    _description='Atributo de una tarea de integracion'
    name=fields.Char('Atributo')
    valor=fields.Char('Valor')

class intregrador_sap_partner(models.Model):
    _name='integrador_sap.task'
    _description='Tarea de integracion con sap'
    name=fields.Char('Tarea')
    
    
    def sync_partner(self):
        _logger.info('Integrador de Partners')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/business-partners'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['res.partner'].search([('ref','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['name']
                    dic['street']=r['address']
                    dic['phone']=r['phone']
                    dic['mobile']=r['mobile']
                    dic['email']=r['email']
                    partner.write(dic)
                else:
                    dic={}
                    dic['ref']=r['code']
                    dic['name']=r['name']
                    dic['street']=r['address']
                    dic['phone']=r['phone']
                    dic['mobile']=r['mobile']
                    dic['email']=r['email']
                    self.env['res.partner'].create(dic)
    
    def sync_categorias(self):
        _logger.info('Integrador de Categorias')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/item-groups'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['product.category'].search([('code','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['name']
                    partner.write(dic)
                else:
                    dic={}
                    dic['code']=r['code']
                    dic['name']=r['name']
                    self.env['product.category'].create(dic)
    
    
    def sync_vendedores(self):
        _logger.info('Integrador de Vendedores')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            user_field=self.env['integrador_sap.property'].search([('name','=','sap_user_field')],limit=1)
            user_type=self.env['integrador_sap.property'].search([('name','=','sap_user_type')],limit=1)
            url=var.valor+'/sales-employee'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['res.users'].search([('code','=',code)])
                email=r['eMail']
                if not r['eMail']:
                    email=str(r['code'])+'@agrosania.com'
                if partner:
                    dic={}
                    dic['name']=r['name']
                    dic['email']=email
                    dic['login']=email
                    partner.write(dic)
                else:
                    dic={}
                    dic['code']=r['code']
                    dic['name']=r['name']
                    dic['email']=email
                    dic['login']=email
                    dic[user_field.valor]=user_type.valor
                    self.env['res.users'].create(dic)
    
    
    def sync_locations(self):
        _logger.info('Integrador de ubicaciones')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/warehouse'
            response = requests.get(url)
            resultado=json.loads(response.text)
            parent_location=self.env['integrador_sap.property'].search([('name','=','sap_location_parent')],limit=1)
            for r in resultado:
                code=r['warehouseCode']
                location=self.env['stock.location'].search([('code','=',code)])
                if location:
                    dic={}
                    dic['name']=r['warehouseName']
                    location.write(dic)
                else:
                    dic={}
                    dic['code']=r['warehouseCode']
                    dic['name']=r['warehouseName']
                    dic['usage']='internal'
                    dic['location_id']=int(parent_location.valor)
                    self.env['stock.location'].create(dic)

    def sync_pricelist(self):
        _logger.info('Integrador de Listas de precios')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/pricelist'
            response = requests.get(url)
            resultado=json.loads(response.text)
            #parent_location=self.env['integrador_sap.property'].search([('name','=','sap_location_parent')],limit=1)
            for r in resultado:
                code=r['listNumber']
                pricelist=self.env['product.pricelist'].search([('code','=',code)])
                if pricelist:
                    dic={}
                    dic['name']=r['listName']
                    dic['factor']=r['factor']
                    pricelist.write(dic)
                else:
                    dic={}
                    dic['code']=r['listNumber']
                    dic['name']=r['listName']
                    dic['factor']=r['factor']
                    self.env['product.pricelist'].create(dic)
            url=var.valor+'/pricelists-detail'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                product=self.env['product.template'].search([('default_code','=',r['itemCode'])],limit=1)
                if product:
                    pricelist=self.env['product.pricelist'].search([('code','=',r['priceList'])],limit=1)
                    if pricelist:
                        rule=self.env['product.pricelist.item'].search([('product_tmpl_id','=',product.id),('pricelist_id','=',pricelist.id)])
                        if rule:
                            dic={}
                            dic['applied_on']='1_product'
                            dic['compute_price']='fixed'
                            if r['price']>0:
                                dic['fixed_price']=r['price']
                            else:
                                dic['fixed_price']=r['factor']*product.list_price
                            rule.write(dic)
                        else:
                            dic={}
                            dic['product_tmpl_id']=product.id
                            dic['pricelist_id']=pricelist.id
                            dic['applied_on']='1_product'
                            dic['compute_price']='fixed'
                            if r['price']>0:
                                dic['fixed_price']=r['price']
                            else:
                                dic['fixed_price']=r['factor']*product.list_price
                            self.env['product.pricelist.item'].create(dic)

    def sync_product(self):
        _logger.info('Integrador de producto')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/items'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                product=self.env['product.template'].search([('default_code','=',code)])
                if product:
                    dic={}
                    dic['name']=r['name']
                    if r['groupCode']:
                        categ=self.env['product.category'].search([('code','=',r['groupCode'])],limit=1)
                        if categ:
                            dic['categ_id']=categ.id
                    #dic['barcode']=r['barcode']
                    product.write(dic)
                else:
                    dic={}
                    dic['default_code']=r['code']
                    dic['name']=r['name']
                    if r['groupCode']:
                        categ=self.env['product.category'].search([('code','=',r['groupCode'])],limit=1)
                        if categ:
                            dic['categ_id']=categ.id
                    #dic['barcode']=r['barcode']
                    self.env['product.template'].create(dic)