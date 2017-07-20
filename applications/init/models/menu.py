# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B(SPAN("Q"),'M',SPAN("T"),'rax'),XML('&trade;&nbsp;'),
                  _class="navbar-brand",_href=URL('default', 'index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Insight Management'
response.meta.description = 'PracticeGenie is a tool designed to simplify the tracking and reminding of primary care referrals.'
response.meta.keywords = 'EMR, reminders, healthcare'
response.meta.generator = 'Web2py Web Framework'  # software that made this page

## your http://google.com/analytics id
response.google_analytics_id = None

## todo - uncomment on deploy
#response.optimize_css = "concat,minify,inline"
#response.optimize_js = "concat,minify,inline"

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

AUTH_USER_ID = getattr(auth.user, "id", None)
PRACTICE_ID = request.vars["practice"]
PRACTICE = None


def IF_PRACTICE_OWNER(id_):
    return bool(PRACTICE.gm == id_)

IS_PRACTICE_OWNER = None
PRACTICE_MEMBERS = []
PRACTICE_MEMBERS_NOT_ME = PRACTICE_MEMBERS[:]  # todo - change me to gm
try:
    if auth.is_logged_in():
        PRACTICE_MEMBERS_NOT_ME.remove(auth.user.id)
except ValueError:
    pass
IS_PRACTICE_MEMBER = False
PRACTICE_VAR = {}
NOT_GRID = "edit" in request.args or "view" in request.args


@auth.requires(False, requires_login=True)
def ACCESS_DENIED():
    pass

if request.controller in ["settings", "reports", "dashboard"]:
    if not PRACTICE_ID:
        PRACTICE = db(db.practice.members.contains(AUTH_USER_ID or 0)).select().last()
        if not PRACTICE:
            print "Could not find practice for user!"  # fixme access_denied overrides flash
            ACCESS_DENIED()
        PRACTICE_ID = PRACTICE.id
        print "redirecting..."
        redirect(URL(a="init", c="default", f="index", vars=dict(practice=PRACTICE_ID)))
    PRACTICE = db(db.practice.id == PRACTICE_ID).select().last()
    PRACTICE_MEMBERS = PRACTICE.members
    if not PRACTICE:
        print "Dealership doesn't exist!"
        ACCESS_DENIED()
    IS_PRACTICE_OWNER = IF_PRACTICE_OWNER(AUTH_USER_ID)
    IS_PRACTICE_MEMBER = bool(AUTH_USER_ID in PRACTICE_MEMBERS)
    if not IS_PRACTICE_OWNER or not IS_PRACTICE_MEMBER:
        print "You are not a member of this practice!"
        ACCESS_DENIED()

    PRACTICE_VAR = dict(practice=PRACTICE_ID)


response.menu = [
    (T('Business Report'), ('index' == request.function), URL('default', 'index'), []),
    (T('Referral Bucket'), ('referral' in request.args), URL('default', 'bucket', args=['referral']), []),  # https://web2py.wordpress.com/tag/active-menu/
    (T('Lab Order Bucket'), ('lab_order' in request.args), URL('default', 'bucket', args=['lab_order']), []),
    (T('DI Order Bucket'), ('di_order' in request.args), URL('default', 'bucket', args=['di_order']), []),
    #(T('QUARR/HEIDIS'), False, URL('bucket', 'quarr_heidis'), []),
    (T('Manage'), (request.controller == 'manage'), URL('manage', 'provider'), []),
]

DEVELOPMENT_MENU = False

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
          (T('This App'), False, '#', [
              (T('Design'), False, URL('admin', 'default', 'design/%s' % app)),
              LI(_class="divider"),
              (T('Controller'), False,
               URL(
               'admin', 'default', 'edit/%s/controllers/%s.py' % (app, ctr))),
              (T('View'), False,
               URL(
               'admin', 'default', 'edit/%s/views/%s' % (app, response.view))),
              (T('DB Model'), False,
               URL(
               'admin', 'default', 'edit/%s/models/db.py' % app)),
              (T('Menu Model'), False,
               URL(
               'admin', 'default', 'edit/%s/models/menu.py' % app)),
              (T('Config.ini'), False,
               URL(
               'admin', 'default', 'edit/%s/private/appconfig.ini' % app)),
              (T('Layout'), False,
               URL(
               'admin', 'default', 'edit/%s/views/layout.html' % app)),
              (T('Stylesheet'), False,
               URL(
               'admin', 'default', 'edit/%s/static/css/web2py-bootstrap3.css' % app)),
              (T('Database'), False, URL(app, 'appadmin', 'index')),
              (T('Errors'), False, URL(
               'admin', 'default', 'errors/' + app)),
              (T('About'), False, URL(
               'admin', 'default', 'about/' + app)),
              ]),
          ('web2py.com', False, '#', [
             (T('Download'), False,
              'http://www.web2py.com/examples/default/download'),
             (T('Support'), False,
              'http://www.web2py.com/examples/default/support'),
             (T('Demo'), False, 'http://web2py.com/demo_admin'),
             (T('Quick Examples'), False,
              'http://web2py.com/examples/default/examples'),
             (T('FAQ'), False, 'http://web2py.com/AlterEgo'),
             (T('Videos'), False,
              'http://www.web2py.com/examples/default/videos/'),
             (T('Free Applications'),
              False, 'http://web2py.com/appliances'),
             (T('Plugins'), False, 'http://web2py.com/plugins'),
             (T('Recipes'), False, 'http://web2pyslices.com/'),
             ]),
          (T('Documentation'), False, '#', [
             (T('Online book'), False, 'http://www.web2py.com/book'),
             LI(_class="divider"),
             (T('Preface'), False,
              'http://www.web2py.com/book/default/chapter/00'),
             (T('Introduction'), False,
              'http://www.web2py.com/book/default/chapter/01'),
             (T('Python'), False,
              'http://www.web2py.com/book/default/chapter/02'),
             (T('Overview'), False,
              'http://www.web2py.com/book/default/chapter/03'),
             (T('The Core'), False,
              'http://www.web2py.com/book/default/chapter/04'),
             (T('The Views'), False,
              'http://www.web2py.com/book/default/chapter/05'),
             (T('Database'), False,
              'http://www.web2py.com/book/default/chapter/06'),
             (T('Forms and Validators'), False,
              'http://www.web2py.com/book/default/chapter/07'),
             (T('Email and SMS'), False,
              'http://www.web2py.com/book/default/chapter/08'),
             (T('Access Control'), False,
              'http://www.web2py.com/book/default/chapter/09'),
             (T('Services'), False,
              'http://www.web2py.com/book/default/chapter/10'),
             (T('Ajax Recipes'), False,
              'http://www.web2py.com/book/default/chapter/11'),
             (T('Components and Plugins'), False,
              'http://www.web2py.com/book/default/chapter/12'),
             (T('Deployment Recipes'), False,
              'http://www.web2py.com/book/default/chapter/13'),
             (T('Other Recipes'), False,
              'http://www.web2py.com/book/default/chapter/14'),
             (T('Helping web2py'), False,
              'http://www.web2py.com/book/default/chapter/15'),
             (T("Buy web2py's book"), False,
              'http://stores.lulu.com/web2py'),
             ]),
          (T('Community'), False, None, [
             (T('Groups'), False,
              'http://www.web2py.com/examples/default/usergroups'),
              (T('Twitter'), False, 'http://twitter.com/web2py'),
              (T('Live Chat'), False,
               'http://webchat.freenode.net/?channels=web2py'),
              ]),
        ]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
