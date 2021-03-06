# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from phytobase import model
from repoze.what import predicates
from phytobase.controllers.secure import SecureController
from phytobase.model import DBSession, metadata
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController

from phytobase.lib.base import BaseController
from phytobase.controllers.error import ErrorController
from phytobase.model import *
from sprox.formbase import AddRecordForm
from tg import tmpl_context
from tg import validate
from datetime import datetime


import tw2.tinymce
import tw2.jquery 
import tw2.core as twc
import tw2.dynforms
import tw2.forms
from tw2.forms import TableForm, TextField,CalendarDatePicker,SingleSelectField, DataGrid
from tw2.sqla import DbFormPage
from tw2.jqplugins.select2 import * 
from tw2.forms.datagrid import Column




from phytobase.controllers.experiments import ExperimentController


# autoExperimentField = AutoCompleteField(
#                    id='experiments',
#                    completionURL = 'fetch_experiments',
#                    fetchJSON = True,
#                    minChars = 1)

# autoOwnerField = AutoCompleteField(
#                    id='owner',
#                    completionURL = 'fetch_users',
#                    fetchJSON = True,
#                    minChars = 1)

class AddFraction(tw2.dynforms.CustomisedTableForm):
    entity = model.Fraction
    id = tw2.forms.HiddenField()
    code = tw2.forms.TextField(validator=twc.Required)
    title = tw2.forms.TextField()
    comment = tw2.forms.TextField()
    description = tw2.tinymce.TinyMCEWidget(
        mce_options = dict(
            mode = 'exact',
            elements = 'description',
            width = '100%',
            height = '10em',
            ))
    # __model__ = Fraction
    # __omit_fields__ = [
    #     'id', 'add_date'
    #     ]
    # code = TextField
    # title = TextField
    # comment = TextField
    # description = TinyMCE(
    #             mce_options = dict(
    #                 mode = 'exact',
    #                 elements = 'description',
    #                 width = '100%',
    #                 height = '10em',
    #             ),
    #             id = 'description',
    #         )
    # experiments = autoExperimentField
    # owner = autoOwnerField
#add_fraction_form = AddFraction(DBSession)


__all__ = ['RootController']


class RootController(BaseController):
    """
    The root controller for the PhytoBase application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)
    error = ErrorController()
    experiments = ExperimentController(DBSession)


    @expose('json')
    def fetch_fractions(self, **named):
        query=named.get("q")
        if query:
            rows = DBSession.query(Fraction).filter(Fraction.code.contains(query)).limit(5).all()
        else:
            rows = DBSession.query(Fraction).limit(5).all()
        return dict(data=rows)

    @expose('json')
    def fetch_experiments(self):
        rows = DBSession.query(Experiment.code).all()
        return dict(data=rows)

    @expose('json')
    def fetch_users(self):
        rows = DBSession.query(User.user_name).all()
        return dict(data=rows)

    @expose('phytobase.templates.index')
    def index(self):
        """Handle the front-page."""
     #   molecules = DBSession.query( Molecule ).order_by( Molecule.title )

        return dict(
            page='index',
            fractions = fractions,
    #        molecules = molecules,
            )

    @expose('phytobase.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('phytobase.templates.widget')
    def addfraction(self):
        """Add fraction."""
        w = AddFraction()
        return dict(widget=w,page='addfraction')

  
    @expose('phytobase.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)


    @expose('phytobase.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('phytobase.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('phytobase.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)




    # Fractions management

    @expose( )
    @validate(
#        form=add_fraction_form,
        error_handler=index,
    )
    def add_fraction( self, code, **named ):
        """Create a new movie record"""
        new = Fraction(
            code = code,
            add_date = datetime.now(),
        )

        if 'title' in named:
            new.title=named['title']
        if 'comment' in named:
            new.comment=named['comment']
        if 'mass' in named:
            new.mass=named['mass']
        if 'mass_left' in named:
            new.mass_left=named['mass_left']

        # Checking if the experiment exists
        if 'description' in named:
            query = DBSession.query(Experiment).filter_by(code=named['experiments'])
            if query.count() != 0:
                experiment_id = query.one()
                new.experiments.append (experiment_id)

        # Checking if the owner exists
        if 'owner' in named:
            query = User.by_user_name(named['owner'])#DBSession.query(User).filter_by(user_name=named['owner'])

            if query != None:
                new.owner.append(query)


        DBSession.add( new )
        flash( '''Added fraction: %s'''%( code, ))
        redirect( './index' )
