from odoo import models, api, fields, _
import hashing_passwords as hp


class Account(models.Model):
    _name = 'mosquitto.account'
    _description = 'Mosquitto Account'
    _rec_name = 'username'

    username = fields.Char(index=True, required=True)
    reset_password = fields.Char()
    pw = fields.Char()
    is_super = fields.Selection(selection=[('1', 'Yes'), ('0','No')],
                default='0', db_column='super', index=True, required=True)

    _sql_constraints = [
        ('username_uniq', 'UNIQUE(username)', _('This MQTT username is already used!')),
    ]


    @api.model
    def create(self, vals):
        reset_password = vals.get('reset_password')
        if reset_password:
            vals['pw'] = hp.make_hash(reset_password)
            vals.pop('reset_password')
        return super(Account, self).create(vals)


    @api.multi
    def write(self, vals):
        reset_password = vals.get('reset_password')
        if reset_password:
            vals['pw'] = hp.make_hash(reset_password)
            vals.pop('reset_password')
        return super(Account, self).write(vals)



class Topic(models.Model):
    _name = 'mosquitto.topic'
    name = fields.Char(index=True)
    description = fields.Text()


class ACL(models.Model):
    _name = 'mosquitto.acl'
    _rec_name = 'username_id'

    username_id = fields.Many2one('mosquitto.account', required=True,
                                  string='Login', ondelete='cascade')
    username = fields.Char(index=True, related='username_id.username', store=True,
                        readonly=True)
    topic_id = fields.Many2one('mosquitto.topic',
                                ondelete='set null', string='Select Topic',)
    topic = fields.Char(required=True, index=True)
    rw = fields.Selection(selection=[
                            ('1', 'Read only'),
                            ('2', 'Write only'),
                            ('3', 'Read Write')
                    ], string='Permission', index=True, required=True)



    @api.onchange('topic_id')
    def on_change_topic_id(self):
        self.ensure_one()
        if self.topic_id:
            self.topic = self.topic_id.name
            # Reset preselected topic
            self.topic_id = None
