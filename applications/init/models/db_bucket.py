db.define_table("patient",
    Field('first_name'),
    Field('last_name'),
    Field('date_of_birth', 'date'),
    auth.signature,
)

#db.patient.first_name.widget = SQLFORM.widgets.autocomplete(request, db.patient.first_name, limitby=(0, 10), min_length=0, distinct=True)
#db.patient.last_name.widget = SQLFORM.widgets.autocomplete(request, db.patient.last_name, limitby=(0, 10), min_length=0, distinct=True)
#db.patient.date_of_birth.widget = SQLFORM.widgets.autocomplete(request, db.patient.date_of_birth, limitby=(0, 10), min_length=0, distinct=True)  # according to the souce, at_beginning True uses field.like(<beginning>%), where as False uses field.contains(<any part>)


db.define_table("site",
    Field('name'),
    Field('phone', requires=IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$')),
    Field('fax', requires=IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$')),
    Field('address'),
    Field('city'),
    Field('district', label="State"),  # should not use reserved keywords like state
    Field('postal_code', label="Zip Code"),  # base label off of subdomain, ie canada.practicegiene.md, then use province
    Field('country', default="USA", readable=False, writable=False),
    auth.signature,
)

db.define_table("provider",
    Field('first_name'),
    Field('last_name'),
    Field('title', requires=IS_IN_SET(["DO", "MD", "NP", "PA"])),
    Field('site', "reference site", requires=IS_IN_DB(db, db.site, '%(name)s')),
    Field('email', requires=IS_EMAIL()),
    Field('phone', requires=IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$')),
    Field('ext', requires=IS_EMPTY_OR(IS_INT_IN_RANGE(0, 10000))),
    auth.signature,
)

db.define_table('referral',
    Field('patient', 'reference patient', requires=IS_IN_DB(db, db.patient, '%(last_name)s, %(first_name)s'), readable=False, writable=False),
    Field('order_date', 'date', default=request.now, readable=False, writable=False),  # change to dt # customize https://www.youtube.com/watch?v=nk5YEP5r-UQ
    Field('ordering_provider', 'reference provider', requires=IS_IN_DB(db, db.provider, '%(last_name)s, %(first_name)s %(title)s')),
    Field('appointment_date', 'date', default=request.now),
    Field('referral_destination', "reference site", requires=IS_IN_DB(db, db.site, '%(name)s')),  # 1st arg can be db or query set: db.person.name.requires = IS_IN_DB(db(db.person.id>10), 'person.id', '%(name)s')
    Field('urgent', 'boolean'),
    Field('conclusion', readable=False, writable=False, requires=IS_IN_SET([('deleted', 'Delete Referral'), ('received', "Referral Received"), ('missed', "Appointment Missed"), ('other', "Other Reason (In Notes)")], zero=None), widget=SQLFORM.widgets.radio.widget),
    auth.signature,
)

db.define_table('outbox',
    Field('referral', 'reference referral'),
    Field('status', requires=IS_IN_SET(["new", "sending", "failed", "sent"])),
    Field('attempts', 'integer', default=0),
    auth.signature,
)

#IMPORTANT - always set not required fields to default = "", or else != operator in queries will return wrong values #https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI