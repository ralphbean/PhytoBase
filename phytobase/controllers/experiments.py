# -*- coding: utf-8 -*-
"""Experiment Controller"""



from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from phytobase import model
from repoze.what import predicates
from phytobase.controllers.secure import SecureController
from phytobase.model import DBSession, metadata
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from tg.controllers import RestController, redirect
from phytobase.lib.base import BaseController
from phytobase.controllers.error import ErrorController
from phytobase.model import *
from sprox.formbase import AddRecordForm
from tg import tmpl_context
from tg import validate
from datetime import datetime


from tg.decorators import paginate

from sqlalchemy import asc, desc
import sqlalchemy as sa
import tw2.tinymce
import tw2.jquery as twj
import tw2.core as twc
import tw2.dynforms as twd
import tw2.forms as twf
from tw2.forms import TableForm, TextField,CalendarDatePicker,SingleSelectField, DataGrid
from tw2.sqla import DbFormPage
from tw2.jqplugins.select2 import * 
from tw2.forms.datagrid import Column


from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.formbase import EditableForm, AddRecordForm
from sprox.fillerbase import TableFiller, EditFormFiller

from formencode.validators import Int, NotEmpty, DateConverter, DateValidator

import genshi


class FractionField(Select2AjaxSingleSelectField):
    attrs = dict(style='width: 400px')
    options = []
    opts = dict(
        placeholder="Select fractions",
        multiple=True,
        ajax=dict(
            url="/fetch_fractions",
            dataType="json",
            data=twc.js_callback(
                """
                function (term, page) {
                    return {
                        q: term, // search term
                
                    };
                }
                """),
            results=twc.js_callback(
                """
                function (data, page) {
                    return {results: data.data};
                }
                """),
            ),
        formatSelection=twc.js_callback(
            """
            function (row) {
                return row.code;
            }
            """),
        formatResult=twc.js_callback(
            """
            function (row) {
                return row.code;
            }
            """),
   )

class ExperimentWidget(twd.GrowingGridLayout):
    id = twf.HiddenField()
    code = FractionField()
#    code = twf.TextField()

class AddEditExperiment(twd.CustomisedTableForm):

    title = twf.TextField()
    
    action = '/experiments'    
    multipart = False
    methot = "PUT"
    entity = model.Experiment
    id = twf.HiddenField()
    code = twf.TextField(validator=twc.Required)
    comment = twf.TextField()
    description = tw2.tinymce.TinyMCEWidget(
        mce_options = dict(
            mode = 'exact',
            elements = 'description',
            width = '100%',
            height = '10em',
            ))
    fractions = ExperimentWidget(fields=[Fraction.id,Fraction.code])
#     owner = autoOwnerField


# class ExperimentIndex(tw2.sqla.DbListPage):
#     entity = model.Experiment
#     title = "Experiments"
#     newlink = tw2.forms.LinkField(link='/experiments/new', text='New', value=1)
#     class child(tw2.dynforms.GrowingGridLayout):
# #        code = tw2.forms.LabelField()
#         id = tw2.forms.LinkField(link='/experiments/experiments?id=$', text='Edit', label="Operations")
#         code = tw2.forms.LinkField(link='/experiments/experiments?id=$id', text='$', label="Code")

# class GridWidget(SQLAjqGridWidget):
#     id = 'grid_widget'
#     entity = model.Experiment
#     excluded_columns = ['id']
#     prmFilter = {'stringResult': True, 'searchOnEnter': False}
#     pager_options = {"del": False,"edit": False, "search": False, "refresh": False, "add": False }
#     options = {
#         'url': '/experiments/db',
#         'rowNum':15,
#         'rowList':[15,30,50],
#         'viewrecords':True,
#         'imgpath': 'scripts/jqGrid/themes/green/images',
#         'width': 900,
#         'height': 'auto',
#     }   

# experiments_grid = DataGrid(fields=[
#         ('Code','code'),
#         ('Action', lambda obj:genshi.Markup('<a href="%s">Edit</a>' % url('/experiments/edit', params=dict(id=obj.id))))
#         ])


__all__ = ['ExperimentController']


class ExperimentController(CrudRestController):

    model = Experiment

    @expose('phytobase.templates.widget')
    def new(self,*args, **kw):
        w = AddEditExperiment()
        return dict(widget=w,page="new",values=dict())

    @expose('phytobase.templates.widget')
    def edit(self,experiment_id,*args, **kw):
        print(request)
        query = DBSession.query(Experiment).filter_by(id=experiment_id).one()
        w = AddEditExperiment()# values=dict(title="Heyho"))
 
        values = query
        return dict(widget=w,page="edit",values=values)

    # class edit_form_type(EditableForm):
    #     __model__ = Experiment
    #     __omit_fields__ = ['id']

    # class edit_filler_type(EditFormFiller):
    #     __model__ = Experiment

    class table_type(TableBase):
        __model__ = Experiment
        __omit_fields__ = ['id']

    class table_filler_type(TableFiller):
        __model__ = Experiment

    @validate({'code':NotEmpty}, error_handler=new)
    @expose()
    def post(self,**kw):
        experiment = DBSession.query(Experiment).get(kw.get('id'))
        if not experiment :
            experiment=Experiment()
        experiment.fractions=[]
        for f_id in kw.get('fractions'):
            experiment.fractions.append(DBSession.query(Fraction).get(f_id))

        experiment.title = kw.get('title')
        experiment.code = kw.get('code')
        experiment.description = kw.get('description')
        experiment.comment = kw.get('comment')
        DBSession.flush()
        flash( '''Modified experiment: %s'''%( kw.get('code') ))
        redirect( '/experiments' )
    

            

    @expose( )
    def add( self, code, **named ):
        """Create a new record"""
        new = Experiment(
            code = code,
            add_date = datetime.now(),
        )

        if 'title' in named:
            new.title=named['title']
        if 'comment' in named:
            new.comment=named['comment']

        # Checking if the experiment exists
        if 'description' in named:
            for fraction in named['fractions']:
                query = DBSession.query(Fraction).filter_by(code=fraction)
                if query.count() != 0:
                    fraction_id = query.one()
                    new.fractions.append (fraction_id)

        # Checking if the owner exists
        if 'owner' in named:
            query = User.by_user_name(named['owner'])#DBSession.query(User).filter_by(user_name=named['owner'])

            if query != None:
                new.owner.append(query)


        DBSession.add( new )
        flash( '''Added experiment: %s'''%( code, ))
        redirect( '/experiments/new' )
