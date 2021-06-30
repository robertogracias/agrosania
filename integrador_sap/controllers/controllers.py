# -*- coding: utf-8 -*-
# from odoo import http


# class /home/representaciones/sucursales(http.Controller):
#     @http.route('//home/representaciones/sucursales//home/representaciones/sucursales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/representaciones/sucursales//home/representaciones/sucursales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/representaciones/sucursales.listing', {
#             'root': '//home/representaciones/sucursales//home/representaciones/sucursales',
#             'objects': http.request.env['/home/representaciones/sucursales./home/representaciones/sucursales'].search([]),
#         })

#     @http.route('//home/representaciones/sucursales//home/representaciones/sucursales/objects/<model("/home/representaciones/sucursales./home/representaciones/sucursales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/representaciones/sucursales.object', {
#             'object': obj
#         })
