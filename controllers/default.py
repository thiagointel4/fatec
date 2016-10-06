# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from datetime import datetime, timedelta


def index():
    cursos = db((db.curso.instrutor == db.auth_user.id) & (db.curso.ativo == True) & (db.curso.data_ini > datetime.now())).select()
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
@auth.requires(auth.has_membership('administrador'))
def curso():
    db.curso.instrutor.requires = IS_IN_DB(db((db.auth_membership.user_id == db.auth_user.id) & (db.auth_membership.group_id == auth.id_group('instrutor'))), 'auth_user.id', '%(first_name)s %(last_name)s')
    #db.curso.instrutor.writable = False
    #db.curso.instrutor.readable = False
    db.auth_user._format = '%(first_name)s %(last_name)s'
    form = SQLFORM.grid(db.curso, searchable=False, details=False, csv=False,
                        fields=[db.curso.instrutor, db.curso.titulo, db.curso.data_ini, db.curso.data_fim, db.curso.sala, db.curso.vaga, db.curso.ativo, db.curso.descricao])
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('aluno'))
def cad_curso():
    cursos = db((db.curso.instrutor == db.auth_user.id) & (db.curso.ativo == True) & (db.curso.data_ini > datetime.now())).select()
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
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def aluno():
    if auth.has_membership('administrador'):
        alunos = db((db.auth_user.id == db.ownership.users) & (db.ownership.curso == db.curso.id)).select(orderby=db.curso.titulo)
        insts = db((db.auth_membership.group_id == auth.id_group('instrutor')) & (db.auth_membership.user_id == db.auth_user.id) & (db.auth_user.id == db.curso.instrutor)).select()
        instrutores = dict()
        for i in insts:
            instrutores[str(i.auth_user.id)] = '{0} {1}'.format(i.auth_user.first_name, i.auth_user.last_name)
    else:
        alunos = db((db.auth_user.id == db.ownership.users) & (db.ownership.curso == db.curso.id) & (db.curso.instrutor == auth.user_id)).select(orderby=db.curso.titulo)

    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def confirma():
    curso = db((db.ownership.curso == db.curso.id) & (db.curso.instrutor == request.args(1)) & (db.ownership.id == request.args(0))).select().first() or redirect(URL('aluno'))
    if curso:
        db(db.ownership.id == request.args(0)).update(status=2)
        db(db.curso.id == curso.curso.id).update(vaga=curso.curso.vaga - 1)
    redirect(URL('default', 'aluno'))


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def desparticipa():
    curso = db((db.ownership.curso == db.curso.id) & (db.curso.instrutor == request.args(1)) & (db.ownership.id == request.args(0))).select().first() or redirect(URL('aluno'))
    if curso:
        db(db.ownership.id == request.args(0)).delete()
        db(db.curso.id == curso.curso.id).update(vaga=curso.curso.vaga + 1)
    redirect(URL('default', 'aluno'))


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def chamada():
    instrutores = db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == auth.id_group('instrutor'))).select(db.auth_user.ALL)
    id_instrutor = auth.user_id
    if request.vars.instrutor and auth.has_membership('administrador'):
        id_instrutor = request.vars.instrutor
        inst_sel = '%(first_name)s %(last_name)s' % db(db.auth_user.id == id_instrutor).select().first()
    cursos = db((db.curso.instrutor == id_instrutor) & (db.curso.ativo == True) & (db.curso.data_ini <= datetime.now().replace(hour=23,minute=59)) & (db.curso.data_fim >= datetime.now().replace(hour=23,minute=59))).select()
    dia = datetime.now().strftime('%d/%m/%Y')
    if session.alerta:
        response.flash = session.alerta
        session.alerta = ''
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def chamada_realizada():
    instrutores = db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == auth.id_group('instrutor'))).select(db.auth_user.ALL)
    id_instrutor = auth.user_id
    if request.vars.instrutor and auth.has_membership('administrador'):
        id_instrutor = request.vars.instrutor
        inst_sel = '%(first_name)s %(last_name)s' % db(db.auth_user.id == id_instrutor).select().first()
    cursos = db((db.curso.instrutor == id_instrutor) & (db.ownership.curso == db.curso.id) & (db.chamada.curso == db.ownership.id)).select(orderby=db.curso.titulo)
    if session.alerta:
        response.flash = session.alerta
        session.alerta = ''
    return locals()


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def salva():
    num = request.args(0) or redirect(URL('chamada'))
    curso = request.args(1)
    if int(num) > 0:
        alunos = request.vars.alunos.split(',')
        ownerships = db((db.ownership.curso == curso) & (db.ownership.status == 2)).select()
        for o in ownerships:
            if str(o.users) in alunos:
                db.chamada.insert(curso=o.id, chamada=True)
            else:
                db.chamada.insert(curso=o.id, chamada=False)
        session.alerta = 'Chamada Salva'
    else:
        session.alerta = 'Não há aluno para realizar a chamada'
    return URL('default', 'chamada')


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def salva_correcao():
    num = request.args(0) or redirect(URL('chamada_realizada'))
    ownership_id = request.args(1)
    if int(num) > 0:
        alunos = request.vars.alunos.split(',')
        chamadas = db((db.chamada.curso == ownership_id) & (db.ownership.id == db.chamada.curso)).select()
        for o in chamadas:
            if str(o.ownership.users) in alunos:
                db(db.chamada.id == o.chamada.id).update(chamada=True)
            else:
                db(db.chamada.id == o.chamada.id).update(chamada=False)
        session.alerta = 'Chamada Atualizada'
    else:
        session.alerta = 'Não há aluno para realizar a chamada'
    return URL('default', 'chamada_realizada')


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def get_aluno():
    head = '''<table class="table table-striped table-borded aluno_chamada">
                <thead>
                <tr>
                    <th>Aluno</th>
                    <th>presença</th>
                </tr>
                </thead>
                <tbody>{0}</tbody>
              </table>
              <div class="text-center" style="width:100%;">
                <button onclick="$(this).attr('disabled',true);salva_aluno();" class="btn btn-success">Salvar</button>
              </div>
    '''
    body = ''
    resp = ''
    id_instrutor = auth.user_id
    if request.vars.instrutor and auth.has_membership('administrador'):
        id_instrutor = request.vars.instrutor
        inst_sel = '%(first_name)s %(last_name)s' % db(db.auth_user.id == id_instrutor).select().first()
    cursos = db((db.curso.instrutor == id_instrutor) & (db.curso.id == request.args(0)) & (db.ownership.curso == db.curso.id) & (db.ownership.status == 2) & (db.ownership.users == db.auth_user.id)).select()
    for c in cursos:
        body += '''<tr>
                        <td>{0} {1}</td>
                        <td><input type="checkbox" value="{2}" style="width:20px;height:20px;" /></td>
                    </tr>
        '''.format(c.auth_user.first_name, c.auth_user.last_name, c.auth_user.id)
    if cursos:
        if db((db.ownership.curso == request.args(0)) & (db.chamada.curso == db.ownership.id)).isempty():
            resp = head.format(body)
        else:
            resp = '<h2>Chamada já realizada</h2>'
    else:
        resp = '<h2>Não tem nenhum aluno</h2>'

    return resp


@auth.requires_login()
@auth.requires(auth.has_membership('instrutor') or auth.has_membership('administrador'))
def get_aluno_correcao():
    head = '''<table class="table table-striped table-borded aluno_chamada">
                <thead>
                <tr>
                    <th>Aluno</th>
                    <th>presença</th>
                </tr>
                </thead>
                <tbody>{0}</tbody>
              </table>
              <div class="text-center" style="width:100%;">
                <button onclick="$(this).attr('disabled',true);salva_aluno();" class="btn btn-success">Salvar</button>
              </div>
    '''
    body = ''
    resp = ''
    id_instrutor = auth.user_id
    if request.vars.instrutor and auth.has_membership('administrador'):
        id_instrutor = request.vars.instrutor
        inst_sel = '%(first_name)s %(last_name)s' % db(db.auth_user.id == id_instrutor).select().first()
    cursos = db((db.curso.instrutor == id_instrutor) & (db.chamada.id == request.args(0)) & (db.ownership.curso == db.curso.id) & (db.chamada.curso == db.ownership.id) & (db.ownership.users == db.auth_user.id)).select()
    for c in cursos:
        body += '''<tr>
                        <td>{0} {1}</td>
                        <td><input type="checkbox" {3} value="{2}" style="width:20px;height:20px;" /></td>
                    </tr>
        '''.format(c.auth_user.first_name, c.auth_user.last_name, c.auth_user.id, 'checked' if c.chamada.chamada else '')
    if cursos:
        resp = head.format(body)

    return resp
