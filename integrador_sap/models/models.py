# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
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

class integrador_partner(models.Model):
    _inherit='res.partner'
    nrc=fields.Char("NRC")
    nit=fields.Char("NIT")
    giro=fields.Char("Giro")
    razon_social=fields.Char("Razón social")
    taxcode=fields.Char("taxcode")

class integrador_property(models.Model):
    _name='integrador_sap.property'
    _description='Atributo de una tarea de integracion'
    name=fields.Char('Atributo')
    valor=fields.Char('Valor')
    
class integrador_ruta(models.Model):
    _name='integrador_sap.ruta'
    _description='Ruta'
    codigo=fields.Char('Codigo')
    name=fields.Char('Ruta')
    
class integrador_taxcode(models.Model):
    _name='integrador_sap.taxcode'
    _description='Impuesto'
    codigo=fields.Char('Codigo')
    name=fields.Char('Impuesto')
    Rate=fields.Char('Rate')
    
class integrador_taxcode(models.Model):
    _name='integrador_sap.gestion'
    _description='Gestion'
    codigo=fields.Char('Codigo')
    name=fields.Char('Name')

class integrador_sucursal(models.Model):
    _name='integrador_sap.sucursal'
    _description='Sucursal'
    name=fields.Char('Sucursal')
    codigo=fields.Char('Codigo')

class integrador_orderline(models.Model):
    _inherit='sale.order.line'
    user_id = fields.Many2one('res.users', required=False,string='Vendedor')

class integrador_order(models.Model):
    _inherit='sale.order'
    code=fields.Integer("Codigo")
    ruta_id = fields.Many2one('integrador_sap.ruta', required=False,string='Ruta')
    sucursal_id = fields.Many2one('integrador_sap.sucursal', required=False,string='Ruta')
    gestion=fields.Many2one('integrador_sap.gestion', required=False,string='gestion')
    
    def sync_sap(self):
        _logger.info('Integrador de ordenes')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            for r in self:
                dic={}
                dic['clientCode']=r.partner_id.ref
                dic['clientName']=r.partner_id.name
                dic['documentDate']=r.date_order
                dic['documentDueDate']=r.validity_date
                dic['salesPersonCode']=r.user_id.code
                dic['comments']=r.note
                dic['nrc']=r.partner_id.nrc
                dic['nit']=r.partner_id.nit
                dic['giro']=r.partner_id.giro
                dic['fechaDocumento']='2021-08-13'
                dic['razonSocial']=r.partner_id.razon_social
                dic['direccion']=r.partner_shipping_id.street
                dic['sucursal']=r.sucursal_id.codigo
                dic['ruta']=r.ruta_id.codigo
                dic['responsable']=r.user_id.code
                dic['getsion']=r.gestion.codigo
                lines=[]
                for l in r.order_line:
                    line={}
                    line['itemCode']=l.product_id.default_code
                    line['quantity']=l.product_uom_qty
                    for t in l.tax_id:
                        line['taxCode']=t.description
                    line['price']=l.price_unit
                    line['discountPercent']=l.discount
                    line['salesPersonCode']=l.user_id.code
                    line['text']=l.name
                    lines.append(line)
                dic['orderDetail']=lines
                encabezado = {"content-type": "application/json"}
                json_datos = json.dumps(dic)
                result = requests.post(var+'/sales-order',data = json_datos, headers=encabezado)
            print(r.text)


class intregrador_sap_partner(models.Model):
    _name='integrador_sap.task'
    _description='Tarea de integracion con sap'
    name=fields.Char('Tarea')
    
    
    def sync_sucursales(self):
        _logger.info('Integrador de sucursales')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/sucursales'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['integrador_sap.sucursal'].search([('codigo','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['name']
                    partner.write(dic)
                else:
                    dic={}
                    dic['codigo']=r['code']
                    dic['name']=r['name']
                    self.env['integrador_sap.sucursal'].create(dic)

    def sync_ruta(self):
        _logger.info('Integrador de rutas')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/rutas'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['integrador_sap.ruta'].search([('codigo','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['name']
                    partner.write(dic)
                else:
                    dic={}
                    dic['codigo']=r['code']
                    dic['name']=r['name']
                    self.env['integrador_sap.ruta'].create(dic)
    
    def sync_gestiones(self):
        _logger.info('Integrador de gestiones')
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/gestion-venta'
            response = requests.get(url)
            resultado=json.loads(response.text)
            for r in resultado:
                code=r['code']
                partner=self.env['integrador_sap.gestion'].search([('codigo','=',code)])
                if partner:
                    dic={}
                    dic['name']=r['description']
                    partner.write(dic)
                else:
                    dic={}
                    dic['codigo']=r['code']
                    dic['name']=r['description']
                    self.env['integrador_sap.gestion'].create(dic)
                    
    
    
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
                    dic['giro']=r['giro']
                    dic['nit']=r['nit']
                    dic['nrc']=r['nrc']
                    partner.write(dic)
                else:
                    dic={}
                    dic['ref']=r['code']
                    dic['name']=r['name']
                    dic['street']=r['address']
                    dic['phone']=r['phone']
                    dic['mobile']=r['mobile']
                    dic['email']=r['email']
                    dic['giro']=r['giro']
                    dic['nit']=r['nit']
                    dic['nrc']=r['nrc']
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
                    dic['type']='product'
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
                    dic['type']='product'
                    if r['groupCode']:
                        categ=self.env['product.category'].search([('code','=',r['groupCode'])],limit=1)
                        if categ:
                            dic['categ_id']=categ.id
                    #dic['barcode']=r['barcode']
                    self.env['product.template'].create(dic)

    def sync_stock(self):
        var=self.env['integrador_sap.property'].search([('name','=','sap_url')],limit=1)
        if var:
            url=var.valor+'/items-stock'
            ubicaciones={}
            lst=self.env['stock.location'].search([('usage','=','internal')])
            for l in lst:
                if l.code:
                    ubicaciones[l.code]=l
            response = requests.get(url)
            resultado=json.loads(response.text)
            inventory=self.env['stock.inventory'].create({'name':'Syncronizacion:'+str(fields.Datetime.now())})
            inventory.action_start()
            for r in resultado:
                code=r['itemCode']
                product=self.env['product.product'].search([('default_code','=',code)])
                if product:
                    location=ubicaciones[r['warehouseCode']]
                    if location:
                        dic={}
                        dic['product_id']=product.id
                        dic['location_id']=location.id
                        dic['inventory_id']=inventory.id
                        dic['product_qty']=r['onHand']
                        self.env['stock.inventory.line'].create(dic)
            inventory.action_validate()