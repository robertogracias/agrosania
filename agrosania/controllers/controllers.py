# -*- coding: utf-8 -*-
# from odoo import http
import logging
import pprint
import werkzeug
import json
import requests

from odoo import http
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

