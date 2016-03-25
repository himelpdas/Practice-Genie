@auth.requires_login()
def settings():
    form = SQLFORM(db.provider)
    return dict(form=form)