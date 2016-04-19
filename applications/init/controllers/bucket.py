import on_validation
from Paginater import Paginater


@auth.requires_login()
def referral():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Under Construction!")
    form = SQLFORM.factory(db.patient, db.referral, hidden={"_update": 0}, buttons=[
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])  # to combine multiple tables you can use SQLFORM.factory (See: One form for multiple tables) or form[0].insert (see: Adding extra form elements to SQLFORM)

    update_id = int(request.post_vars['_update'] or -1)  # cannot get hidden fields from form.vars
    if form.process(onvalidation=on_validation.beautify_name).accepted:
        patient_id = db.patient.update_or_insert(**db.patient._filter_fields(form.vars))
        form.vars.patient = patient_id  # this is a field in referral
        if not update_id:  # 0 is false
            db.referral.insert(**db.referral._filter_fields(form.vars))
            response.flash = 'Referral added.'
        else:
            # todo - test for permission if user has right to update id
            db(db.referral.id == update_id).update(**db.referral._filter_fields(form.vars))
            response.flash = 'Referral updated.'
    elif form.errors:
        response.flash_modal = dict(flash="#object_modal", update_id=update_id)

    query_set = db(db.referral.id > 0)
    paginater = Paginater(request, query_set, db)
    rows = query_set.select(db.referral.ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, left=[  # left join ensures query_set.count() == len(rows)
        db.patient.on(db.referral.patient == db.patient.id),
        db.site.on(db.referral.referral_destination == db.site.id),
        db.provider.on(db.referral.ordering_provider == db.provider.id),
    ], limitby=paginater.limitby, orderby=paginater.orderby)  # explicitly select all http://stackoverflow.com/questions/7782717/web2py-dal-multiple-left-joins

    return dict(form=form, rows=rows, paginater=paginater)
