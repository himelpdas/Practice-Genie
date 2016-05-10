import on_validation
from Paginater import Paginater
import json
import os

@auth.requires_login()
#@minify  # todo - use on deploy
def referral():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    archive = "archive" in request.args

    # OBJECT FORM
    form = SQLFORM.factory(db.patient, db.referral, _id="object_form", hidden={"_update": 0}, buttons=[
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])  # to combine multiple tables you can use SQLFORM.factory (See: One form for multiple tables) or form[0].insert (see: Adding extra form elements to SQLFORM)
    update_id = int(request.post_vars['_update'] or -1)  # cannot get hidden fields from form.vars
    if form.process(formname='object_form', onvalidation=on_validation.beautify_name).accepted:
        patient_id = db.patient.update_or_insert(**db.patient._filter_fields(form.vars))
        form.vars.patient = patient_id  # this is a field in referral
        if patient_id:  # patient id will be None if no changes were detected for update or insert
            if not update_id:  # 0 is false
                referral_id = db.referral.insert(**db.referral._filter_fields(form.vars))
                db.referral_outbox.validate_and_insert(referral=referral_id, status="new")
                response.flash = 'Referral added.'
            else:
                # todo - test for permission if user has right to update id
                db(db.referral.id == update_id).update(**db.referral._filter_fields(form.vars))
                response.flash = 'Referral updated.'
        else:
            response.flash = 'No changes were made.'
    elif form.errors:
        response.flash_modal = dict(flash="#object_modal", update_id=update_id)

    # conclusion FORM
    db.referral.conclusion.readable = db.referral.conclusion.writable = True  #DO THIS AFTER conclusion FORM
    db.referral.conclusion.default = "received"
    conclusion_form = SQLFORM.factory(db.referral['conclusion'], _id="conclusion_form", hidden={"_conclude": 0},
        buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right")]
    )
    close_id = int(request.post_vars['_conclude'] or -1)
    if conclusion_form.process(formname="conclusion_form").accepted:
        if close_id:
            db(db.referral.id == close_id).update(**conclusion_form.vars)
        response.flash = "Referral marked as %s." % conclusion_form.vars["conclusion"]

    # OUTGOING FAX
    outgoing_form = SQLFORM.factory(_id="outgoing_form", _class="pull-left", hidden={'_outgoing': json.dumps(None)},
        # could've used jquery form but SQLFORM provides _formkey to prevent double submission. FORM does not have .process(), it's more of a HTML helper class
        buttons=[
            TAG.button(SPAN(_class="glyphicon glyphicon glyphicon-print") + " " + "Send Faxes",
                       _type="submit", _class="btn btn-success btn-sm")]
        )
    if not archive and outgoing_form.process(formname="outgoing_form").accepted:
        outgoing_ids = json.loads(request.post_vars["_outgoing"] or "null")
        if outgoing_ids:
            outgoing_referrals = db(db.referral.id.belongs(outgoing_ids)).select(
                db.referral.ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, db.referral_outbox.ALL,
                left=[
                    # VALIDATE that rows belong to group
                    db.patient.on(db.referral.patient == db.patient.id),
                    db.site.on(db.referral.referral_destination == db.site.id),
                    db.provider.on(db.referral.ordering_provider == db.provider.id),
                    db.referral_outbox.on(db.referral.id == db.referral_outbox.referral),
                ])

            for row in outgoing_referrals:
                row.referral_outbox.update_record(status="sending")
                row.referral_outbox.status = "sent"
                row.referral_outbox.attempts += 1  # fake change for email

            body = response.render('__doc_templates/fax.html', dict(rows=outgoing_referrals))

            if mail.send(to=['himel.p.das@gmail.com'],
                         subject='Practice Genie MD Outstanding Orders ' + str(request.now),
                         message=body):
                send_success = True
            else:
                send_success = False
            for row in outgoing_referrals:
                if not send_success:
                    row.referral_outbox.attempts -= 1
                    row.referral_outbox.sent = "failed"
                row.referral_outbox.update_record(attempts=row.referral_outbox.attempts, status=row.referral_outbox.status)

    # QUERY
    query = db.referral.id > 0
    if archive:
        query &= db.referral.conclusion != "deleted"
    else:
        query &= db.referral.conclusion == None  # You can't compare NULL values using <> in SQL https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI

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
    rows = query_set.select(db.referral.ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, db.referral_outbox.ALL, left=[  # left join ensures query_set.count() == len(rows)
        db.patient.on(db.referral.patient == db.patient.id),
        db.site.on(db.referral.referral_destination == db.site.id),
        db.provider.on(db.referral.ordering_provider == db.provider.id),
        db.referral_outbox.on(db.referral.id == db.referral_outbox.referral),
    ], limitby=paginater.limitby, orderby=paginater.orderby)  # explicitly select all http://stackoverflow.com/questions/7782717/web2py-dal-multiple-left-joins

    # NOTES
    note_form = SQLFORM.factory(db.referral_note, formname="note_form", _class="form-horizontal", hidden={'_request': 0}, buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right")],)
    if note_form.process().accepted:
        request_id = int(request.post_vars['_request'] or -1)
        if request_id:
            db.referral_note.insert(request=request_id, **db.referral_note._filter_fields(note_form.vars))
            response.flash = "Note entered."
        else:
            response.flash = "Hidden ID field missing."
    for row in rows:
        row.referral_notes = db(db.referral_note.request == row.referral.id).select(db.auth_user.ALL, db.referral_note.ALL, join=[db.auth_user.on(db.auth_user.id == db.referral_note.created_by)])  # left inner protects against None auth_user

    return dict(form=form, conclusion_form=conclusion_form, outgoing_form=outgoing_form, rows=rows, paginater=paginater, archive=archive, note_form=note_form)

'''
@auth.requires_login()  # https://groups.google.com/forum/#!topic/web2py/zzLVxaQZn7U
def download():
    return response.stream(open(os.path.join(request.folder, 'private_static', os.path.normpath(request.args(0)))))
'''