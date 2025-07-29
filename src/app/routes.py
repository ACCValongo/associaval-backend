from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, AssociationForm, ActivityForm
from app.models import User, Association, Activity
from flask_login import login_user, current_user, logout_user, login_required
import json

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Início")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and not current_user.is_admin:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(email=form.email.data, password=hashed_password, is_admin=form.is_admin.data)
        db.session.add(user)
        db.session.commit()
        flash("A sua conta foi criada com sucesso! Agora pode fazer login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Registar", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("manage_associations"))
        else:
            return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for("manage_associations"))
            else:
                return redirect(url_for("home"))
        else:
            flash("Login sem sucesso. Por favor, verifique o email e a palavra-passe", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/admin/associations", methods=["GET", "POST"])
@login_required
def manage_associations():
    if not current_user.is_admin:
        flash("Não tem permissão para aceder a esta página.", "danger")
        return redirect(url_for("home"))
    
    associations = Association.query.all()
    form = AssociationForm()
    
    if form.validate_on_submit():
        # Converter categorias selecionadas para JSON
        activity_categories_json = json.dumps(form.activity_categories.data) if form.activity_categories.data else None
        
        association = Association(name=form.name.data, address=form.address.data, 
                                  phone=form.phone.data, email=form.email.data,
                                  social_media=form.social_media.data, description=form.description.data,
                                  activity_categories=activity_categories_json, 
                                  other_activities=form.other_activities.data)
        db.session.add(association)
        db.session.commit()
        
        # Criar utilizador para a associação
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(email=form.email.data, password=hashed_password, is_admin=False, association_id=association.id)
        db.session.add(user)
        db.session.commit()
        
        flash("Associação e utilizador criados com sucesso!", "success")
        return redirect(url_for("manage_associations"))
        
    return render_template("manage_associations.html", title="Gerir Associações", associations=associations, form=form)

@app.route("/association/<int:association_id>/edit", methods=["GET", "POST"])
@login_required
def edit_association(association_id):
    association = Association.query.get_or_404(association_id)
    if not current_user.is_admin and (not current_user.association_id or current_user.association_id != association.id):
        flash("Não tem permissão para editar esta associação.", "danger")
        return redirect(url_for("home"))
    
    form = AssociationForm()
    if form.validate_on_submit():
        # Converter categorias selecionadas para JSON
        activity_categories_json = json.dumps(form.activity_categories.data) if form.activity_categories.data else None
        
        association.name = form.name.data
        association.address = form.address.data
        association.phone = form.phone.data
        association.email = form.email.data
        association.social_media = form.social_media.data
        association.description = form.description.data
        association.activity_categories = activity_categories_json
        association.other_activities = form.other_activities.data
        db.session.commit()
        flash("Associação atualizada com sucesso!", "success")
        return redirect(url_for("manage_associations"))
    elif request.method == "GET":
        form.name.data = association.name
        form.address.data = association.address
        form.phone.data = association.phone
        form.email.data = association.email
        form.social_media.data = association.social_media
        form.description.data = association.description
        form.other_activities.data = association.other_activities
        # Converter JSON de volta para lista para o formulário
        if association.activity_categories:
            try:
                form.activity_categories.data = json.loads(association.activity_categories)
            except:
                form.activity_categories.data = []
    return render_template("edit_association.html", title="Editar Associação", form=form, association=association)

@app.route("/association/<int:association_id>/delete", methods=["POST"])
@login_required
def delete_association(association_id):
    association = Association.query.get_or_404(association_id)
    if not current_user.is_admin:
        flash("Não tem permissão para apagar esta associação.", "danger")
        return redirect(url_for("home"))
    db.session.delete(association)
    db.session.commit()
    flash("Associação apagada com sucesso!", "success")
    return redirect(url_for("manage_associations"))

@app.route("/association/<int:association_id>/activities", methods=["GET", "POST"])
@login_required
def manage_activities(association_id):
    association = Association.query.get_or_404(association_id)
    if not current_user.is_admin and (not current_user.association_id or current_user.association_id != association.id):
        flash("Não tem permissão para gerir as atividades desta associação.", "danger")
        return redirect(url_for("home"))
    
    activities = Activity.query.filter_by(association_id=association.id).all()
    form = ActivityForm()
    
    if form.validate_on_submit():
        activity = Activity(name=form.name.data, description=form.description.data,
                            date=form.date.data, location=form.location.data,
                            association_id=association.id)
        db.session.add(activity)
        db.session.commit()
        flash("Atividade criada com sucesso!", "success")
        return redirect(url_for("manage_activities", association_id=association.id))
        
    return render_template("manage_activities.html", title="Gerir Atividades", activities=activities, form=form, association=association)

@app.route("/activity/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
def edit_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if not current_user.is_admin and (not current_user.association_id or current_user.association_id != activity.association.id):
        flash("Não tem permissão para editar esta atividade.", "danger")
        return redirect(url_for("home"))
    
    form = ActivityForm()
    if form.validate_on_submit():
        activity.name = form.name.data
        activity.description = form.description.data
        activity.date = form.date.data
        activity.location = form.location.data
        db.session.commit()
        flash("Atividade atualizada com sucesso!", "success")
        return redirect(url_for("manage_activities", association_id=activity.association.id))
    elif request.method == "GET":
        form.name.data = activity.name
        form.description.data = activity.description
        form.date.data = activity.date
        form.location.data = activity.location
    return render_template("edit_activity.html", title="Editar Atividade", form=form, activity=activity)

@app.route("/activity/<int:activity_id>/delete", methods=["POST"])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if not current_user.is_admin and (not current_user.association_id or current_user.association_id != activity.association.id):
        flash("Não tem permissão para apagar esta atividade.", "danger")
        return redirect(url_for("home"))
    db.session.delete(activity)
    db.session.commit()
    flash("Atividade apagada com sucesso!", "success")
    return redirect(url_for("manage_activities", association_id=activity.association.id))

