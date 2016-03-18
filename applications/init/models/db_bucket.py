db.define_table("patient",
    Field('first_name'),
    Field('last_name'),
    Field('date_of_birth', 'date'),
    auth.signature,
)

db.define_table("site",
    Field('name'),
    Field('address'),
    Field('zip_code'),
    auth.signature,
)

db.define_table("provider",
    Field('first_name'),
    Field('last_name'),
    Field('title', requires=IS_IN_SET(["DO", "MD", "NP"])),
    Field('site', "reference:site"),
    auth.signature,
)

db.define_table('referral',
    Field('patient', 'reference:patient', readable=False, writable=False),
    Field('order_date', 'date', default=request.now, readable=False, writable=False),  # customize https://www.youtube.com/watch?v=nk5YEP5r-UQ
    Field('ordering_provider', 'reference:provider', requires=IS_IN_DB(db, db.provider)),
    Field('appointment_date', 'date', default=request.now),
    Field('referral_destination', "reference:site", requires=IS_IN_DB(db, db.site)),  # 1st arg can be db or query set: db.person.name.requires = IS_IN_DB(db(db.person.id>10), 'person.id', '%(name)s')
    auth.signature,
)
