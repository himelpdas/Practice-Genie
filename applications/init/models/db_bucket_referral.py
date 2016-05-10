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

db.define_table('referral_outbox',
    Field('referral', 'reference referral'),
    Field('status', requires=IS_IN_SET(["new", "sending", "failed", "sent"])),
    Field('attempts', 'integer', default=0),
    auth.signature,
)

#IMPORTANT - always set not required fields to default = "", or else != operator in queries will return wrong values #https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI

db.define_table('referral_note',
    Field('request','reference referral', readable=False, writable=False),
    Field('note'),
    Field('is_log', 'boolean', required=True),
    auth.signature,
)