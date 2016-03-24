#@auth.requires_login()
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
    if form.process().accepted:
        patient_id = db.client.insert(**db.patient._filter_fields(form.vars))
        form.vars.patient = patient_id  # this is a field in referral
        referral_id = db.address.insert(**db.referral._filter_fields(form.vars))
        response.flash='Thanks for filling the form'

    return dict(form=form)

def test():
    x=SQLFORM.factory(db.patient, db.referral)
    return dict(form=x)