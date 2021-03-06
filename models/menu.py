# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.logo = A(IMG(_src=URL('static', 'images/fatec.png'), _height="40"),
                  _class="navbar-brand", _href="http://www.fatecsjc.edu.br/",
                  _id="web2py-logo")
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
    ('Inicio', False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True


# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. remove in production
# ----------------------------------------------------------------------------------------------------------------------

def _():
    # ------------------------------------------------------------------------------------------------------------------
    # shortcuts
    # ------------------------------------------------------------------------------------------------------------------
    app = request.application
    ctr = request.controller
    # ------------------------------------------------------------------------------------------------------------------
    # useful links to internal and external resources
    # ------------------------------------------------------------------------------------------------------------------
    response.menu += [

    ]
    if auth.is_logged_in() and auth.has_membership('administrador'):
        response.menu.append(('Usuários', False, URL('default', 'administrador'), []))
        response.menu.append(('Cursos', False, URL('default', 'curso'), []))
        response.menu.append(('Confirmação', False, URL('default', 'aluno'), []))
        response.menu.append(('Chamada', False, URL('default', 'chamada'), []))
        response.menu.append(('Chamada Realizada', False, URL('default', 'chamada_realizada'), []))
    if auth.is_logged_in() and auth.has_membership('instrutor'):
        response.menu.append(('Chamada', False, URL('default', 'chamada'), []))
        response.menu.append(('Chamada Realizada', False, URL('default', 'chamada_realizada'), []))
    if auth.is_logged_in() and auth.has_membership('aluno'):
        response.menu.append(('Meus Cursos', False, URL('default', 'cad_curso'), []))


if DEVELOPMENT_MENU:
    _()

if "auth" in locals():
    auth.wikimenu()
