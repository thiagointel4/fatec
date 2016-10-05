# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager
from datetime import datetime

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()


# valida cpf e cnpj
class IS_CPF_OR_CNPJ(object):
    def __init__(self, format=False, error_message=T('Número incorreto!')):
        self.error_message = error_message
        self.format = format

    def __call__(self, value):
        try:
            cl = str(''.join(c for c in value if c.isdigit()))

            if len(cl) == 11:
                cpf = cl
                cnpj = None
            elif len(cl) == 14:
                cpf = None
                cnpj = cl
            else:
                return value, self.error_message

            if cpf:
                def calcdv(numb):
                    result = int()
                    seq = reversed(
                        ((range(9, -1, -1) * 2)[:len(numb)])
                    )
                    for digit, base in zip(numb, seq):
                        result += int(digit) * int(base)
                    dv = result % 11
                    return (dv - 10) and dv or 0

                numb, xdv = cpf[:-2], cpf[-2:]

                dv1 = calcdv(numb)
                dv2 = calcdv(numb + str(dv1))
                if '%d%d' % (dv1, dv2) == xdv:
                    return self.doformat(cpf) if self.format else cpf, None
                else:
                    return cpf, T('CPF inválido')

            elif cnpj:

                intmap = map(int, cnpj)
                validate = intmap[:12]

                prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                while len(validate) < 14:
                    r = sum([x * y for (x, y) in zip(validate, prod)]) % 11
                    f = 11 - r if r > 1 else 0
                    validate.append(f)
                    prod.insert(0, 6)

                if validate == intmap:
                    return self.doformat(cnpj) if self.format else cnpj, None

                else:
                    return cnpj, T('CNPJ inválido')

        except:
            return value, self.error_message

    def doformat(self, value):
        if len(value) == 11:
            result = value[0:3] + '.' + value[3:6] + '.' + value[6:9] + \
                     '-' + value[9:11]
        elif len(value) == 14:
            result = value[0:2] + '.' + value[2:5] + '.' + value[5:8] + \
                     '/' + value[8:12] + '-' + value[12:14]
        else:
            result = value
        return result


# acrescenta campos a tabela auth_user
auth.settings.extra_fields['auth_user'] = [
    Field('ident', 'string', length=20, requires=IS_CPF_OR_CNPJ())
]

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False)


# define todos os que se cadastram como aluno
def give_editor_permission(form):
    group_id = auth.id_group("aluno")
    auth.add_membership(group_id, auth.user.id)


auth.settings.register_onaccept = give_editor_permission

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = None

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)


if db(db.auth_user).isempty():
    try:
        db.auth_user.insert(
            password=db.auth_user.password.validate('admin123')[0],
            email='admin@admin.com',
            first_name='Admin',
            last_name='Admin'
        )

        db.executesql("insert into auth_group(id,role, description) values ({0}, '{1}', '{2}');".format(1, 'administrador', 'Administração'))
        db.executesql("insert into auth_group(id,role, description) values ({0}, '{1}', '{2}');".format(2, 'instrutor', 'Instrutor do curso'))
        db.executesql("insert into auth_group(id,role, description) values ({0}, '{1}', '{2}');".format(3, 'aluno', 'Aluno'))

        db.executesql("insert into auth_membership(id,user_id, group_id) values ({0}, '{1}',{2});".format(1, 1, 1))

    except Exception as e:
        print e

Cursos = db.define_table('curso',
                         Field('titulo', label='Titulo'),
                         Field('data_ini', 'datetime', label='Início'),
                         Field('data_fim', 'datetime', label='Término'),
                         Field('sala', 'integer', label='Sala'),
                         Field('vaga', 'integer', label='Vagas'),
                         Field('instrutor', 'reference auth_user', label='Instrutor'),  # so pode ser user group instrutor
                         # Field('participante', 'reference auth_user', label='Participantes'),
                         Field('ativo', 'boolean', default=False, label='Confirmado'),
                         Field('descricao', label='Descrição'))

db.define_table('ownership',
                Field('curso', 'reference curso'),
                Field('users', 'reference auth_user'),
                Field('status', 'integer', label='Status'))

db.define_table('chamada',
                Field('curso', 'reference ownership', label='Curso'),
                Field('chamada', 'boolean', default=False, notnull=True, label='Chamada'),
                Field('data_chamada', 'datetime', notnull=True, default=datetime.now(), label='Data')
                )
# incriçao ou seja o selecionaro o curso e houver vagas o user vai marcar o curso#curso é muitosa
# para muito
# relacionar aluno aos cursos
# listar todos os user que teem campo curso igual ao curso
