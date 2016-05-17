# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


import on_validation
from Paginater import Paginater
import json
#from Minify import minify

def __validate_parent_id(*args):
    pass

@auth.requires_login()
#@minify  # todo - use on deploy
def bucket():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    archive = "archive" in request.args
    try:
        bucket = {'referral', 'di_order', 'lab_order'}.intersection(request.args).pop()
    except KeyError:
        raise HTTP(404)

    # OBJECT FORM
    form = SQLFORM.factory(db.patient, db[bucket], _id="object_form", hidden={"_update": 0}, buttons=[
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])  # to combine multiple tables you can use SQLFORM.factory (See: One form for multiple tables) or form[0].insert (see: Adding extra form elements to SQLFORM)
    update_id = int(request.post_vars['_update'] or -1)  # cannot get hidden fields from form.vars
    if form.process(formname='object_form', onvalidation=on_validation.beautify_name).accepted:
        patient_id = db.patient.update_or_insert(**db.patient._filter_fields(form.vars))
        form.vars.patient = patient_id  # this is a field in referral
        if patient_id:  # patient id will be None if no changes were detected for update or insert
            if not update_id:  # 0 is false
                bucket_row_id = db[bucket].insert(**db[bucket]._filter_fields(form.vars))
                db[bucket+'_outbox'].validate_and_insert(parent=bucket_row_id, status="new")  # FIXME
                response.flash = bucket.capitalize()+' added.'
                db[bucket+'_note'].insert(parent=bucket_row_id, note=response.flash, is_log=True)
            else:
                # todo - test for permission if user has right to update id
                db(db[bucket].id == update_id).update(**db[bucket]._filter_fields(form.vars))
                response.flash = bucket.capitalize()+' updated.'
                db[bucket+'_note'].insert(parent=update_id, note=response.flash, is_log=True)
        else:
            response.flash = 'No changes were made.'
    elif form.errors:
        response.flash_modal = dict(flash="#object_modal", update_id=update_id)

    # conclusion FORM
    db[bucket].conclusion.readable = db[bucket].conclusion.writable = True  #DO THIS AFTER conclusion FORM
    db[bucket].conclusion.default = "received"
    conclusion_form = SQLFORM.factory(db[bucket].conclusion, _id="conclusion_form", hidden={"_conclude": 0},
        buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right")]
    )
    close_id = int(request.post_vars['_conclude'] or -1)
    if conclusion_form.process(formname="conclusion_form").accepted:
        if close_id:
            db(db[bucket].id == close_id).update(**conclusion_form.vars)
        response.flash = "%s marked as %s." % (bucket.capitalize(), conclusion_form.vars["conclusion"])

    # OUTGOING FAX
    outgoing_form = SQLFORM.factory(_id="outgoing_form", _class="pull-left", hidden={'_outgoing': json.dumps(None)},
        # could've used jquery form but SQLFORM provides _formkey to prevent double submission. FORM does not have .process(), it's more of a HTML helper class
        buttons=[
            TAG.button(SPAN(_class="glyphicon glyphicon glyphicon-print") + " " + "Send Faxes",
                       _type="submit", _class="btn btn-success btn-sm")]
        )
    if not archive and outgoing_form.process(formname="outgoing_form").accepted:
        outgoing_ids = json.loads(request.post_vars["_outgoing"] or "null")
        print outgoing_ids
        if outgoing_ids:
            outgoing_bucket_rows = db(db[bucket].id.belongs(outgoing_ids)).select(
                db[bucket].ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, db[bucket+'_outbox'].ALL,
                left=[
                    # VALIDATE that rows belong to group
                    db.patient.on(db[bucket].patient == db[bucket].id),
                    db.site.on(db[bucket].destination == db.site.id),
                    db.provider.on(db[bucket].ordering_provider == db.provider.id),
                    db[bucket+'_outbox'].on(db[bucket].id == db[bucket+'_outbox'].parent),
                ])

            for row in outgoing_bucket_rows:
                row[bucket+'_outbox'].update_record(status="sending")
                row[bucket+'_outbox'].status = "sent"
                row[bucket+'_outbox'].attempts += 1  # fake change for email

            body = response.render('__doc_templates/fax.html', dict(rows=outgoing_bucket_rows, bucket=bucket))

            if mail.send(to=['himel.p.das@gmail.com'],
                         subject='Practice Genie MD Outstanding Orders ' + str(request.now),
                         message=body):
                send_success = True
            else:
                send_success = False
            for row in outgoing_bucket_rows:
                if not send_success:
                    row[bucket+'_outbox'].attempts -= 1
                    row[bucket+'_outbox'].sent = "failed"
                row[bucket+'_outbox'].update_record(attempts=row[bucket+'_outbox'].attempts, status=row[bucket+'_outbox'].status)

    # QUERY
    query = db[bucket].id > 0
    if archive:
        query &= db[bucket].conclusion != "deleted"
    else:
        query &= db[bucket].conclusion == None  # You can't compare NULL values using <> in SQL https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI

    # SEARCH
    if request.vars.patient:
        patient = map(lambda each: each.strip(), request.vars.patient.split(","))
        patient_last = patient[0]
        if patient_last:  # can be "", patient_last, so just search latter
            query &= db.patient.last_name.like(patient_last, case_sensitive=False)
        if len(patient) > 1:
            patient_first = patient[1]
            query &= db.patient.first_name.like(patient_first, case_sensitive=False)

    query_set = db(query)

    # PAGE
    paginater = Paginater(request, query_set, db)
    rows = query_set.select(db[bucket].ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, db[bucket+'_outbox'].ALL, left=[  # left join ensures query_set.count() == len(rows)
        db.patient.on(db[bucket].patient == db.patient.id),
        db.site.on(db[bucket].destination == db.site.id),
        db.provider.on(db[bucket].ordering_provider == db.provider.id),
        db[bucket+'_outbox'].on(db[bucket].id == db[bucket+'_outbox'].parent),
    ], limitby=paginater.limitby, orderby=paginater.orderby)  # explicitly select all http://stackoverflow.com/questions/7782717/web2py-dal-multiple-left-joins

    # NOTES
    note_form = SQLFORM.factory(db[bucket+'_note'], formname="note_form", _class="form-horizontal", hidden={'_add_note_to': 0}, buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right")],)
    if note_form.process().accepted:
        parent_id = int(request.post_vars['_add_note_to'] or -1)
        if parent_id:
            db[bucket+'_note'].insert(parent=parent_id, **db[bucket+'_note']._filter_fields(note_form.vars))
            response.flash = "Note was entered to the %s." % bucket
        else:
            response.flash = "Hidden ID field missing."
    for row in rows:
        row_notes = db(db[bucket+'_note'].parent == row[bucket].id).select(db.auth_user.ALL, db[bucket+'_note'].ALL, join=[db.auth_user.on(db.auth_user.id == db[bucket+'_note'].created_by)])  # left inner protects against None auth_user
        row[bucket + "_notes"] = row_notes.find(lambda each: not each[bucket+'_note'].is_log)
        row[bucket + "_logs"] = row_notes.find(lambda each: each[bucket+'_note'].is_log)
    return dict(form=form, conclusion_form=conclusion_form, outgoing_form=outgoing_form, rows=rows, paginater=paginater, archive=archive, note_form=note_form, bucket=bucket)

'''
@auth.requires_login()  # https://groups.google.com/forum/#!topic/web2py/zzLVxaQZn7U
def download():
    return response.stream(open(os.path.join(request.folder, 'private_static', os.path.normpath(request.args(0)))))
'''
