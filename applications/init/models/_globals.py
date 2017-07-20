# Objects here will be accessible across views, controllers, and any models alphabetically after
PHONE_VALIDATOR = \
    IS_MATCH('^\(*\+*[1-9]{0,3}\)*-*[1-9]{0,3}[-. /]*\(*[2-9]\d{2}\)*[-. /]*\d{3}[-. /]*\d{4} *e*x*t*\.* *\d{0,4}$',
             error_message='Invalid telephone number')