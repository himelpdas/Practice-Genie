import on_validation

@auth.requires_login()
def referral():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    #response.flash = T("Under Construction!")
    form = SQLFORM.factory(db.patient, db.referral, buttons = [
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])  # to combine multiple tables you can use SQLFORM.factory (See: One form for multiple tables) or form[0].insert (see: Adding extra form elements to SQLFORM)

    if form.process(onvalidation=on_validation.beautify_name).accepted:
        patient_id = db.patient.update_or_insert(**db.patient._filter_fields(form.vars))
        form.vars.patient = patient_id  # this is a field in referral
        referral_id = db.referral.insert(**db.referral._filter_fields(form.vars))
        response.flash='Referral successfully added'

    rows = db(db.referral.id > 0).select(db.referral.ALL, db.patient.ALL, db.site.ALL, db.provider.ALL, join=[
        db.patient.on(db.referral.patient == db.patient.id),
        db.site.on(db.referral.referral_destination == db.site.id),
        db.provider.on(db.referral.ordering_provider == db.provider.id),
    ])  # explicitly select all http://stackoverflow.com/questions/7782717/web2py-dal-multiple-left-joins
    return dict(form=form, rows=rows)
