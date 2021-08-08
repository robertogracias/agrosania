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

