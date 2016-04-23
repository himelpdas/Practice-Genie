import on_validation
from Paginater import Paginater
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

    #OBJECT FORM
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
                db.referral.insert(**db.referral._filter_fields(form.vars))
                response.flash = 'Referral added.'
            else:
                # todo - test for permission if user has right to update id
                db(db.referral.id == update_id).update(**db.referral._filter_fields(form.vars))
                response.flash = 'Referral updated.'
        else:
            response.flash = 'No changes were made.'
    elif form.errors:
        response.flash_modal = dict(flash="#object_modal", update_id=update_id)

    #OUTCOME FORM
    db.referral.outcome.readable = db.referral.outcome.writable = True  #DO THIS AFTER OUTCOME FORM
    db.referral.outcome.default = "received"
    outcome_form = SQLFORM.factory(db.referral['outcome'], _id="outcome_form", hidden={"_close": 0},
        buttons=[TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right")]
    )
    close_id = int(request.post_vars['_close'] or -1)
    if outcome_form.process(formname="outcome_form").accepted:
        if close_id:
            db(db.referral.id == close_id).update(**outcome_form.vars)
        response.flash = "Referral Deleted."

    #QUERY
    query = (db.referral.id > 0) & (db.referral.outcome == None)  # You can't compare NULL values using <> in SQL https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI
    if request.vars.patient:
        patient = map(lambda each: each.strip(), request.vars.patient.split(","))
        patient_last = patient[0]
        query &= db.patient.last_name.like(patient_last, case_sensitive=False)
        if len(patient) > 1:
            patient_first = patient[1]
            query &= db.patient.first_name.like(patient_first, case_sensitive=False)
    query_set = db(query)
    paginater = Paginater(request, query_set, db)
    rows = query_set.select(db.referral.ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, left=[  # left join ensures query_set.count() == len(rows)
        db.patient.on(db.referral.patient == db.patient.id),
        db.site.on(db.referral.referral_destination == db.site.id),
        db.provider.on(db.referral.ordering_provider == db.provider.id),
    ], limitby=paginater.limitby, orderby=paginater.orderby)  # explicitly select all http://stackoverflow.com/questions/7782717/web2py-dal-multiple-left-joins

    return dict(form=form, outcome_form=outcome_form, rows=rows, paginater=paginater)

'''
@auth.requires_login()  # https://groups.google.com/forum/#!topic/web2py/zzLVxaQZn7U
def download():
    return response.stream(open(os.path.join(request.folder, 'private_static', os.path.normpath(request.args(0)))))
'''