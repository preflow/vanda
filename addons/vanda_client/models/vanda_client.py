# -*- coding: utf-8 -*-
import os
import base64
from jinja2 import Template

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

# -------------------------

# Decode base64 string to text
def base64_to_text(base64_string):
    base64_bytes = base64_string.encode('utf-8')
    text_bytes = base64.b64decode(base64_bytes)
    return text_bytes.decode('utf-8')

# Encode text to base64 string
def text_to_base64(text):
    text_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode('utf-8')

# Render text with Jinja2
def render_with_jinja2(template_text, context):
    template = Template(template_text)
    rendered_text = template.render(context)
    return rendered_text

def process_base64_jinja2(base64_string, context):
    # Step 1: Decode base64 to text
    decoded_text = base64_to_text(base64_string)

    # Step 2: Render text with Jinja2
    rendered_text = render_with_jinja2(decoded_text, context)

    # Step 3: Encode rendered text back to base64
    encoded_base64_string = text_to_base64(rendered_text)

    return encoded_base64_string

# -------------------------

class VandaClientFile(models.Model):
    _name = "vanda.client.file"
    _description = "Vanda Client File"

    name = fields.Char('Name', required=True)  # relative path. E.g. redis/docker-compose.yml
    md5_hash = fields.Char('MD5 Hash', required=True)    
    bin_content = fields.Binary("Bin Content", attachment=True)
    is_template = fields.Boolean("Is Template", default=False)
    vanda_client_id = fields.Many2one('vanda.client', string="Vanda Client", required=True, ondelete='cascade')

# -------------------------

class VandaClient(models.Model):
    _name = "vanda.client"
    _description = "Vanda Client"

    name = fields.Char(required=True)   # Redis Connector
    code = fields.Char(required=True)   # redis (client name in "./clients")
    image = fields.Image(string="Image", max_width=256, max_height=256)
    file_ids = fields.Many2many('vanda.client.file', 'vanda_client_file_rel', string='Files')

    @api.model
    def create(self, vals):
        # add pre-processing
        record_name = vals.get("name", "")
        if not record_name:
            raise ValidationError("Missing preflow name! %s" % vals)

        exist_record = self.search([("name", "=", record_name)], limit=1)
        if exist_record:
            raise ValidationError("Duplicated ID: %s" % record_name)
        return super(VandaClient, self).create(vals)

    @api.model
    def render_files(self, id):
        vanda_client = self.browse(id)
        file_records = vanda_client.file_ids
        result = [
            # {"path": "redis/abc.py", "bin_content": "<base64>"}
        ]
        for file_rec in file_records:
            bin_content = file_rec.bin_content
            if file_rec.is_template:
                # render with jinja2
                bin_content = process_base64_jinja2(
                    base64_string=bin_content.decode("utf-8"), # base64 byte to string
                    context={
                        "vanda_client": vanda_client
                    }
                )
                pass

            result.append({
                "path": file_rec.name, # redis/abc.py => relative path
                "bin_content": bin_content,
            })
            pass
        return result

    @api.model
    def reload_vanda_client_files(self):
        clients_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../clients"))
        child_folders = [f for f in os.listdir(clients_dir) if os.path.isdir(os.path.join(clients_dir, f))]     # redis, postgres, ...
        _logger.info(f"Reload files {child_folders} in directory: {clients_dir}")
        files = plazy.list_files(root=clients_dir,
                            filter_func=lambda x : False if x.count('__pycache__')>=1 else True,
                            is_include_root=False)  # ["redis/docker-compose.yml", ...]
        for childf in child_folders: # redis
            vanda_client = self.search([('code', '=', childf)], limit=1)
            if vanda_client:
                # clear old files
                # SYNC...TODO
                # vanda_client.file_ids
                pass
            pass
        pass
    