@auth.requires_login()
def settings():
    provider_form = SQLFORM(db.provider)
    return dict(provider_form=provider_form)