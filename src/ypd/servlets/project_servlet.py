from functools import wraps

from flask import (current_app, flash, redirect, render_template, request,url_for)
from flask_classy import FlaskView, route
from flask_login import current_user, login_required

from ..form.project_form import EditForm, SubmissionForm
from ..model.project import Provided, Solicited
from ..model.user import User
from .tests import Tests


class ProjectView(FlaskView):
    decorators = [login_required]   #apply login_required to all routes
    class Decorator:
        @classmethod
        def needs_project(cls, func):
            """Decorator for routes that require a project instance
            
            Requires adding two args to the decorated function:
            project (Project): Project requested by user
            """
            @wraps(func)
            def wrapper(*args, **kwargs):
                #whether the project is provided. Booleans are broken due to a bug within Flask, so we have
                #to use an integer instead. Instead of true and false, we'll use truthy and falsy values
                #e.g., 0=False, >1 = True
                is_provided = request.args.get('is_provided', default=0, type=int)
                id = request.args.get('id', default = ' ', type=int) #id of project
                try:
                    if is_provided:
                        kwargs['project'] = Provided.get(id)
                    else:
                        kwargs['project'] = Solicited.get(id)
                except Exception:
                    return 'The requested project could not be found', 404
                current_app.jinja_env.tests['provided'] = Tests.is_provided_test
                return func(*args, **kwargs)
            return wrapper

    @route('/view')
    @Decorator.needs_project
    def view(self, project):        
        return render_template('project.html', project=project, user=current_user)

    @route('/favorite')
    @Decorator.needs_project
    def favorite(self, project):
        """Called when the user favorites or defavorites a project"""
        #Truthy if we want to favorite a project. Falsy if we want to defavorite a project
        favorite = request.args.get('favorite', default=0, type=int)

        if favorite:
            current_user.favorite_project(project)
        else:
            current_user.defavorite_project(project)

        return redirect(url_for('ProjectView:view', id=project.id, 
                                                    is_provided=Tests.is_provided_test(project)))

    # pull data from HTML form
    @route('/archive')
    @Decorator.needs_project
    def archive(self, project):
        """Called when the user archives a project"""
        #Sets Archive flag to True/False
        project.toggle_archived(current_user)

        return redirect(url_for('ProjectView:view', id=project.id,
                                is_provided=Tests.is_provided_test(project)))

    # pull data from HTML form
    @route ('/submit', methods =('GET', 'POST'))  
    def submit(self):
        form = SubmissionForm()

        if form.validate_on_submit():
                projType = form.projType.data
                title = form.title.data
                description = form.description.data

                if projType is None:
                    flash("You must select a project type") #We have to validate radio fields manually
                    return render_template('set_project_data.html', form=form)
                elif projType == form.PROVIDED:
                    project = Provided()
                else:
                    project = Solicited()
                project.post(title, description, current_user)
                return redirect(url_for('IndexView:get',
                                        is_provided=(projType==form.PROVIDED), id=project.id))
        return render_template('set_project_data.html', form=form)

    @route('/edit', methods=('GET', 'POST'))
    @Decorator.needs_project
    def edit(self, project):
        form = EditForm()

        if form.validate_on_submit():
            project.edit(current_user, **form.data)
            return redirect(url_for('ProjectView:view', id=project.id,
                                    is_provided=Tests.is_provided_test(project)))
        else:
            for field in form:
                if hasattr(project, field.name):
                    field.data = getattr(project, field.name)
            return render_template('set_project_data.html', form=form, project=project) 
