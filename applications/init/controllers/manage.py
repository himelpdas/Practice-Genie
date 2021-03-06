import on_validation


@auth.requires_login()
def provider():
    form = SQLFORM(db.provider, buttons=[
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])
    if form.process(onvalidation=on_validation.beautify_name, keepvalues=True).accepted:
        response.flash = 'Provider added successfully'
    elif form.errors:
        response.flash_modal = "#add_provider_modal"

    rows = db(db.provider.id > 0).select(db.site.ALL, db.provider.ALL, join=[db.site.on(db.provider.site == db.site.id)])
    return dict(form=form, rows=rows)


@auth.requires_login()
def provider():
    form = SQLFORM.grid(db.provider)
    return dict(form=form)


@auth.requires_login()
def destination():
    form = SQLFORM.grid(db.destination)
    return dict(form=form)


@auth.requires_login()
def site():
    form = SQLFORM.grid(db.site)
    return dict(form=form)


@auth.requires_login()
def patient():
    form = SQLFORM.grid(db.patient)
    return dict(form=form)


@auth.requires_login()
def user():
    form = SQLFORM.grid(db.auth_user)
    return dict(form=form)


