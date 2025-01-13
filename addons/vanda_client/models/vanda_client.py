# -*- coding: utf-8 -*-
import os
import base64
from jinja2 import Template, Environment, FileSystemLoader, TemplateSyntaxError
import hashlib
import plazy

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

# -------------------------
def is_jinja2_template(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        return False, "File does not exist."
    
    try:
        # Create a Jinja2 environment and load the template
        env = Environment(loader=FileSystemLoader(os.path.dirname(file_path)))
        template_name = os.path.basename(file_path)
        template = env.get_template(template_name)  # Load the template
        
        # Check if the file contains Jinja2-specific syntax
        if any(["{{" in template.source, "{%" in template.source, "{#" in template.source]):
            return True, "Valid Jinja2 template."
        return False, "No Jinja2-specific syntax found, but file is valid."
    except TemplateSyntaxError as e:
        return False, f"TemplateSyntaxError: {e.message} at line {e.lineno}."
    except Exception as e:
        return False, f"Error: {e}"

def calculate_md5(file_path):
    # Create an md5 hash object
    md5_hash = hashlib.md5()
    
    # Open the file in binary mode and read chunks of it
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    # Return the hexadecimal digest of the hash
    return md5_hash.hexdigest()

def file_to_base64(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Read the file's contents
        file_content = file.read()
        
    # Encode the file's contents in base64
    base64_encoded = base64.b64encode(file_content)
    
    # Convert the base64 bytes to a string and return
    return base64_encoded.decode('utf-8')

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
    file_ids = fields.One2many('vanda.client.file', 'vanda_client_id', string='Files')

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
    def sync_src_files(self):
        clients_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../clients"))
        child_folders = [f for f in os.listdir(clients_dir) if os.path.isdir(os.path.join(clients_dir, f))]     # redis, postgres, ...
        _logger.info(f"Sync src files {child_folders} in directory: {clients_dir}")
        files = plazy.list_files(root=clients_dir,
                            filter_func=lambda x : False if x.count('__pycache__')>=1 else True,
                            is_include_root=False)  # ["redis/docker-compose.yml", ...]
        for client_name in child_folders: # redis
            vanda_client = self.search([('code', '=', client_name)], limit=1)
            client_files_on_disk = [f for f in files if f.startswith(client_name)]
            if vanda_client:
                vanda_client_files = vanda_client.file_ids.mapped('name')
                files_insert = list(set(client_files_on_disk) - set(vanda_client_files))
                files_del = list(set(vanda_client_files) - set(client_files_on_disk))
                files_update = [f for f in client_files_on_disk if f in vanda_client_files]
                if files_insert:
                    values = []
                    for fi in files_insert:
                        file_path = os.path.join(clients_dir, fi)
                        # name = fields.Char('Name', required=True)  # relative path. E.g. redis/docker-compose.yml
                        # md5_hash = fields.Char('MD5 Hash', required=True)    
                        # bin_content = fields.Binary("Bin Content", attachment=True)
                        # is_template = fields.Boolean("Is Template", default=False)
                        # vanda_client_id = fields.Many2one('vanda.client', string="Vanda Client", required=True, ondelete='cascade')
                        values.append({
                            "name": fi,     # redis/docker-compose.yml
                            "md5_hash": calculate_md5(file_path=file_path),
                            "bin_content": file_to_base64(file_path=file_path),
                            "is_template": is_jinja2_template(file_path=file_path)[0],
                            "vanda_client_id": vanda_client.id,
                        })
                    new_recs = self.env["vanda.client.file"].create(values)
                    _logger.info(f"[vanda.client.sync_src_files] Created remote files: {files_insert} => {new_recs}")
                    pass

                if files_del:
                    f2del = self.env["vanda.client.file"].search([("vanda_client_id", "=", vanda_client.id), ("name", "in", files_del)])
                    _logger.info(f"[vanda.client.sync_src_files] Deleted remote files: {files_del} => {f2del}")
                    f2del.unlink()
                    pass

                if files_update:
                    f2update = self.env["vanda.client.file"].search([("vanda_client_id", "=", vanda_client.id), ("name", "in", files_update)])
                    for f2up in f2update:
                        local_file_path = os.path.join(clients_dir, f2up.name)
                        local_file_md5_hash = calculate_md5(file_path=local_file_path)
                        updated_file_names = []
                        if local_file_md5_hash == f2up.md5_hash:
                            # matching md5 hash => do nothing
                            pass
                        else:
                            # update the content of the remote file
                            f2up.update({
                                "md5_hash": local_file_md5_hash,
                                "bin_content": file_to_base64(file_path=local_file_path),
                                "is_template": is_jinja2_template(file_path=local_file_path)[0],
                            })
                            updated_file_names.append(f2up.name)
                        _logger.info(f"[vanda.client.sync_src_files] Updated remote files: {updated_file_names}")
                        pass
                    pass
                pass
            pass
        pass
