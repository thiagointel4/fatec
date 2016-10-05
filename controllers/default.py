# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    cursos = db((db.curso.instrutor == db.auth_user.id) & (db.curso.ativo == True)).select()
    return locals()


def user():
    return dict(form=auth())


@cache.action()
def download():
    return response.download(request, db)


def call():
    return service()


@auth.requires_login()
@auth.requires(auth.has_membership('administrador'))
def administrador():
    usuarios = db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == db.auth_group.id) & (db.auth_group.role != 'administrador')).select()
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('administrador'))
def edita_user():
    user_id = request.args(0) or redirect(URL('default', 'administrador'))
    form = SQLFORM(db.auth_user, user_id, readonly=True, fields=['first_name', 'last_name', 'email'], showid=False)
    member_id = db(db.auth_membership.user_id == user_id).select().first().id
    db.auth_membership.user_id.writable = False
    form_membership = SQLFORM(db.auth_membership, member_id, fields=['group_id'], showid=False)
    if form_membership.process().accepted:
        response.flash = 'Atualizado com sucesso'
        redirect(URL('administrador'))
    elif form_membership.errors:
        response.flash = 'form has errors'
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor'))
def curso():
    db.curso.instrutor.default = auth.user_id
    db.curso.instrutor.writable = False
    db.curso.instrutor.readable = False
    cursos = db((db.curso.instrutor == db.auth_user.id) & (db.curso.ativo == True))
    form = SQLFORM.grid(cursos, searchable=False, details=False, csv=False,
                        fields=[db.curso.titulo, db.curso.data_ini, db.curso.data_fim, db.curso.sala, db.curso.vaga, db.curso.ativo, db.curso.descricao])
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('aluno'))
def cad_curso():
    cursos = db((db.curso.instrutor == db.auth_user.id) & (db.curso.ativo == True)).select()
    curso_cad = db((db.ownership.users == auth.user_id) & (db.ownership.curso == db.curso.id)).select(db.curso.ALL)
    lista_ig = []
    cadastrados = []
    for c in cursos:
        if not db((db.ownership.curso == c.curso.id) & (db.ownership.users == auth.user_id)).isempty():
            lista_ig.append(c.curso.id)
            cadastrados.append(c.curso.id)
        for d in curso_cad:
            if c.curso.id != d.id:
                if d.data_fim >= c.curso.data_ini and d.data_fim <= c.curso.data_fim:
                    lista_ig.append(c.curso.id)
                elif d.data_ini <= c.curso.data_ini and d.data_fim >= c.curso.data_fim:
                    lista_ig.append(c.curso.id)
                elif d.data_ini >= c.curso.data_ini and d.data_ini <= c.curso.data_fim:
                    lista_ig.append(c.curso.id)
                elif d.data_ini >= c.curso.data_ini and d.data_fim <= c.curso.data_fim:
                    lista_ig.append(c.curso.id)
    print lista_ig
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('aluno'))
def participa():
    db.ownership.insert(curso=request.args(0), users=request.args(1), status=1)
    redirect(URL('default', 'cad_curso'))


@auth.requires_login()
@auth.requires(auth.has_membership('aluno'))
def desparticipa():
    db((db.ownership.users == request.args(1)) & (db.ownership.curso == request.args(0))).delete()
    redirect(URL('default', 'cad_curso'))
