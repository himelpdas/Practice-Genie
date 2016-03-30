import on_validation

@auth.requires_login()
def provider():
    form = SQLFORM(db.provider, buttons=[
        TAG.button('Cancel', _type="button", _class="btn btn-default-outline btn-sm pull-right", **{'_data-dismiss' : 'modal'}),
        TAG.button('Submit', _type="submit", _class="btn btn-primary btn-sm pull-right", _style="margin-right:5px;"),
    ])
    if form.process(onvalidation=on_validation.beautify_name, keepvalues=True).accepted:
        response.flash='Provider added successfully'
    elif form.errors:
        response.flash_modal = "#add_provider_modal"

    rows = db(db.provider.id > 0).select(db.site.ALL, db.provider.ALL, join=[db.site.on(db.provider.site == db.site.id)])
    return dict(form=form, rows=rows)