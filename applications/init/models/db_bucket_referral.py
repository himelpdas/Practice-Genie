db.define_table(
    'referral',
    *bucket_generic_fields
)

db.define_table(
    'referral_outbox',
    Field('parent', 'reference referral'),
    *bucket_outbox_generic_fields
)

# IMPORTANT - always set not required fields to default = "", or else != operator in queries will return wrong values
# #https://groups.google.com/forum/#!topic/web2py/MgXAPqEGoUI

db.define_table(
    'referral_note',
    Field('parent', 'reference referral'),
    *bucket_note_generic_fields
)
