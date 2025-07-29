from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, AssociationForm, ActivityForm
from app.models import User, Association, Activity
from flask_login import login_user, current_user, logout_user, login_required
import json

@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("manage_associations"))
        else:
            # Redirecionar associações para gestão das suas atividades
            if current_user.association_id:
                return redirect(url_for("manage_activities", association_id=current_user.association_id))
            else:
                return redirect(url_for("logout"))
    return render_template("home.html", title="Início")

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    # Apenas o administrador principal pode criar novas contas de administrador
    if not current_user.is_admin or current_user.email != "accvalongo@gmail.com":
        flash("Apenas o administrador principal pode criar novas contas.", "danger")
        return redirect(url_for("home"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        # Todas as contas criadas através desta rota são de administradores
        user = User(email=form.email.data, password=hashed_password, is_admin=True)
        db.session.add(user)
        try:
            db.session.commit()
            flash("A conta de administrador foi criada com sucesso!", "success")
            return redirect(url_for("manage_users"))
        except Exception as e:
            db.session.rollback()
            flash("Erro ao criar conta. O email pode já estar em uso.", "danger")
    return render_template("register.html", title="Registar Administrador", form=form)

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
        # Verificar se já existe uma associação com este email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash(f"Já existe um utilizador com o email {form.email.data}. Use um email diferente.", "danger")
            return render_template("manage_associations.html", title="Gerir Associações", associations=associations, form=form)
        
        # Converter categorias selecionadas para JSON
        activity_categories_json = json.dumps(form.activity_categories.data) if form.activity_categories.data else None
        # Converter freguesias selecionadas para JSON
        freguesias_json = json.dumps(form.freguesia.data) if form.freguesia.data else None
        
        association = Association(name=form.name.data, address=form.address.data, 
                                  freguesia=freguesias_json,
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
        
        flash(f"Associação '{association.name}' e utilizador criados com sucesso! Email: {form.email.data}", "success")
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
        # Converter freguesias selecionadas para JSON
        freguesias_json = json.dumps(form.freguesia.data) if form.freguesia.data else None
        
        association.name = form.name.data
        association.address = form.address.data
        association.freguesia = freguesias_json
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
        if association.freguesia:
            try:
                form.freguesia.data = json.loads(association.freguesia)
            except:
                form.freguesia.data = []
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
                            activity_type=form.activity_type.data,
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
        activity.activity_type = form.activity_type.data
        db.session.commit()
        flash("Atividade atualizada com sucesso!", "success")
        return redirect(url_for("manage_activities", association_id=activity.association.id))
    elif request.method == "GET":
        form.name.data = activity.name
        form.description.data = activity.description
        form.date.data = activity.date
        form.location.data = activity.location
        form.activity_type.data = activity.activity_type
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


# API Routes para Frontend
@app.route("/api/associations", methods=["GET"])
def api_associations():
    """API endpoint para obter todas as associações"""
    associations = Association.query.all()
    associations_data = []
    
    for association in associations:
        # Converter categorias JSON de volta para lista
        categories = []
        if association.activity_categories:
            try:
                categories = json.loads(association.activity_categories)
            except:
                categories = []
        
        association_data = {
            'id': association.id,
            'name': association.name,
            'address': association.address,
            'phone': association.phone,
            'email': association.email,
            'social_media': association.social_media,
            'description': association.description,
            'activity_categories': categories,
            'other_activities': association.other_activities
        }
        associations_data.append(association_data)
    
    return {'associations': associations_data}

@app.route("/api/activities", methods=["GET"])
def api_activities():
    """API endpoint para obter todas as atividades"""
    activities = Activity.query.all()
    activities_data = []
    
    for activity in activities:
        # Converter a data do formato DD/MM/YYYY para YYYY-MM-DD
        formatted_date = None
        if activity.date:
            try:
                if '/' in activity.date:
                    day, month, year = activity.date.split('/')
                    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    formatted_date = activity.date
            except Exception as e:
                print(f"Erro ao formatar data: {e}")
                formatted_date = None
        
        activity_data = {
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'date': formatted_date,
            'location': activity.location,
            'activity_type': activity.activity_type,
            'association_id': activity.association_id,
            'association_name': activity.association.name if activity.association else None
        }
        activities_data.append(activity_data)
    
    return {'activities': activities_data}

@app.route("/api/association/<int:association_id>", methods=["GET"])
def api_association_detail(association_id):
    """API endpoint para obter detalhes de uma associação específica"""
    association = Association.query.get_or_404(association_id)
    
    # Converter categorias JSON de volta para lista
    categories = []
    if association.activity_categories:
        try:
            categories = json.loads(association.activity_categories)
        except:
            categories = []
    
    # Obter atividades da associação
    activities = Activity.query.filter_by(association_id=association.id).all()
    activities_data = []
    for activity in activities:
        # Converter a data do formato DD/MM/YYYY para YYYY-MM-DD
        formatted_date = None
        if activity.date:
            try:
                if '/' in activity.date:
                    day, month, year = activity.date.split('/')
                    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    formatted_date = activity.date
            except Exception as e:
                print(f"Erro ao formatar data: {e}")
                formatted_date = None
                
        activity_data = {
            'id': activity.id,
            'name': activity.name,
            'description': activity.description,
            'date': formatted_date,
            'location': activity.location
        }
        activities_data.append(activity_data)
    
    association_data = {
        'id': association.id,
        'name': association.name,
        'address': association.address,
        'phone': association.phone,
        'email': association.email,
        'social_media': association.social_media,
        'description': association.description,
        'activity_categories': categories,
        'other_activities': association.other_activities,
        'activities': activities_data
    }
    
    return association_data


# Gestão de Utilizadores (apenas para administradores)
@app.route("/manage_users")
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem gerir utilizadores.", "danger")
        return redirect(url_for("home"))
    
    users = User.query.all()
    return render_template("manage_users.html", title="Gestão de Utilizadores", users=users)

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem editar utilizadores.", "danger")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    
    # Impedir que o administrador se elimine a si próprio
    if user.id == current_user.id:
        flash("Não pode editar a sua própria conta através desta página.", "warning")
        return redirect(url_for("manage_users"))
    
    if request.method == "POST":
        user.email = request.form.get("email")
        
        # Atualizar password apenas se fornecida
        new_password = request.form.get("password")
        if new_password:
            user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        
        try:
            db.session.commit()
            flash(f"Utilizador {user.email} atualizado com sucesso!", "success")
            return redirect(url_for("manage_users"))
        except Exception as e:
            db.session.rollback()
            flash("Erro ao atualizar utilizador. Email pode já estar em uso.", "danger")
    
    return render_template("edit_user.html", title="Editar Utilizador", user=user)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem eliminar utilizadores.", "danger")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    
    # Impedir que o administrador se elimine a si próprio
    if user.id == current_user.id:
        flash("Não pode eliminar a sua própria conta.", "danger")
        return redirect(url_for("manage_users"))
    
    try:
        # Eliminar associação relacionada se existir
        if user.association_id:
            association = Association.query.get(user.association_id)
            if association:
                # Eliminar atividades da associação
                Activity.query.filter_by(association_id=association.id).delete()
                db.session.delete(association)
        
        db.session.delete(user)
        db.session.commit()
        flash(f"Utilizador {user.email} eliminado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao eliminar utilizador.", "danger")
    
    return redirect(url_for("manage_users"))

@app.route("/create_association_user", methods=["GET", "POST"])
@login_required
def create_association_user():
    if not current_user.is_admin:
        flash("Acesso negado. Apenas administradores podem criar utilizadores para associações.", "danger")
        return redirect(url_for("home"))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        association_id = request.form.get("association_id")
        
        # Verificar se email já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Este email já está em uso.", "danger")
            return redirect(url_for("create_association_user"))
        
        # Verificar se associação existe
        association = Association.query.get(association_id)
        if not association:
            flash("Associação não encontrada.", "danger")
            return redirect(url_for("create_association_user"))
        
        # Verificar se associação já tem utilizador
        existing_association_user = User.query.filter_by(association_id=association_id).first()
        if existing_association_user:
            flash("Esta associação já tem um utilizador associado.", "warning")
            return redirect(url_for("create_association_user"))
        
        try:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(
                email=email, 
                password=hashed_password, 
                is_admin=False,
                association_id=association_id
            )
            db.session.add(user)
            db.session.commit()
            flash(f"Utilizador criado com sucesso para a associação {association.name}!", "success")
            return redirect(url_for("manage_associations"))
        except Exception as e:
            db.session.rollback()
            flash("Erro ao criar utilizador.", "danger")
    
    associations = Association.query.all()
    return render_template("create_association_user.html", title="Criar Utilizador para Associação", associations=associations)

