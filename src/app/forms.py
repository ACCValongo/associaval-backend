from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmar Password",
                                     validators=[DataRequired(), EqualTo("password")])
    is_admin = BooleanField("É Administrador?")
    submit = SubmitField("Registar")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Esse email já está registado. Por favor, escolha um diferente.")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Lembrar-me")
    submit = SubmitField("Login")

class AssociationForm(FlaskForm):
    name = StringField("Nome da Associação", validators=[DataRequired(), Length(min=2, max=100)])
    address = StringField("Morada", validators=[DataRequired(), Length(min=5, max=200)])
    phone = StringField("Telefone", validators=[Length(max=20)])
    email = StringField("Email de Contacto", validators=[Email(), Length(max=120)])
    social_media = StringField("Redes Sociais (URL)", validators=[Length(max=200)])
    description = TextAreaField("Descrição da Associação")
    
    # Categorias de atividades com seleção múltipla
    activity_categories = SelectMultipleField(
        "Categorias de Atividades",
        choices=[
            # Cultura
            ('cultura_teatro', '🎭 Cultura - Teatro'),
            ('cultura_danca_tradicional', '🎭 Cultura - Dança tradicional'),
            ('cultura_danca_moderna', '🎭 Cultura - Dança moderna / contemporânea'),
            ('cultura_canto_coral', '🎭 Cultura - Canto coral'),
            ('cultura_banda_filarmonica', '🎭 Cultura - Banda filarmónica'),
            ('cultura_grupo_musical', '🎭 Cultura - Grupo musical / instrumental'),
            ('cultura_grupo_fados', '🎭 Cultura - Grupo de fados'),
            ('cultura_grupo_etnografico', '🎭 Cultura - Grupo etnográfico / folclórico'),
            ('cultura_escrita_criativa', '🎭 Cultura - Escrita criativa'),
            ('cultura_artes_visuais', '🎭 Cultura - Artes visuais (pintura, escultura, fotografia)'),
            ('cultura_cinema_video', '🎭 Cultura - Cinema / vídeo'),
            ('cultura_clube_leitura', '🎭 Cultura - Clube de leitura'),
            ('cultura_popular_tradicoes', '🎭 Cultura - Cultura popular e tradições'),
            ('cultura_artesanato', '🎭 Cultura - Artesanato'),
            
            # Desporto
            ('desporto_futebol', '🏃 Desporto - Futebol'),
            ('desporto_futsal', '🏃 Desporto - Futsal'),
            ('desporto_atletismo', '🏃 Desporto - Atletismo / corrida'),
            ('desporto_ciclismo', '🏃 Desporto - Ciclismo / BTT'),
            ('desporto_karate', '🏃 Desporto - Karaté / artes marciais'),
            ('desporto_natacao', '🏃 Desporto - Natação'),
            ('desporto_basquetebol', '🏃 Desporto - Basquetebol'),
            ('desporto_voleibol', '🏃 Desporto - Voleibol'),
            ('desporto_tenis', '🏃 Desporto - Ténis / padel'),
            ('desporto_dancas_desportivas', '🏃 Desporto - Danças desportivas'),
            ('desporto_ginastica', '🏃 Desporto - Ginástica / aeróbica'),
            ('desporto_caminhadas', '🏃 Desporto - Caminhadas / trilhos'),
            ('desporto_escalada', '🏃 Desporto - Escalada'),
            ('desporto_orientacao', '🏃 Desporto - Orientação'),
            ('desporto_xadrez', '🏃 Desporto - Xadrez'),
            
            # Bem-estar e Saúde
            ('bemestar_yoga', '🧘 Bem-estar - Yoga'),
            ('bemestar_meditacao', '🧘 Bem-estar - Meditação'),
            ('bemestar_reiki', '🧘 Bem-estar - Reiki'),
            ('bemestar_pilates', '🧘 Bem-estar - Pilates'),
            ('bemestar_terapias', '🧘 Bem-estar - Terapias alternativas'),
            ('bemestar_massagem', '🧘 Bem-estar - Massagem'),
            ('bemestar_relaxamento', '🧘 Bem-estar - Aulas de relaxamento'),
            ('bemestar_saude_comunitaria', '🧘 Bem-estar - Saúde comunitária'),
            
            # Intervenção Social e Cidadania
            ('social_voluntariado', '👥 Social - Voluntariado'),
            ('social_terceira_idade', '👥 Social - Apoio à terceira idade'),
            ('social_familias_carenciadas', '👥 Social - Apoio a famílias carenciadas'),
            ('social_apoio_escolar', '👥 Social - Apoio escolar / explicações'),
            ('social_alfabetizacao', '👥 Social - Cursos de alfabetização'),
            ('social_portugues_estrangeiros', '👥 Social - Português para estrangeiros'),
            ('social_literacia_digital', '👥 Social - Literacia digital'),
            ('social_gestao_domestica', '👥 Social - Gestão doméstica'),
            ('social_escuteiros', '👥 Social - Escuteiros'),
            ('social_movimento_juvenil', '👥 Social - Movimento associativo juvenil'),
            ('social_defesa_causas', '👥 Social - Defesa de causas sociais (ambiente, igualdade, inclusão)'),
            
            # Recreio e Lazer
            ('recreio_jogos_mesa', '🎲 Recreio - Jogos de mesa / cartas'),
            ('recreio_tardes_recreativas', '🎲 Recreio - Tardes recreativas'),
            ('recreio_bailes', '🎲 Recreio - Bailes e matinés'),
            ('recreio_convivios_senior', '🎲 Recreio - Convívios sénior'),
            ('recreio_oficinas_criativas', '🎲 Recreio - Oficinas criativas / DIY'),
            ('recreio_jardins_comunitarios', '🎲 Recreio - Jardins comunitários / hortas'),
            ('recreio_fotografia', '🎲 Recreio - Fotografia amadora'),
            ('recreio_modelismo', '🎲 Recreio - Modelismo'),
            ('recreio_cozinha_tradicional', '🎲 Recreio - Cozinha tradicional'),
            
            # Formação / Educação
            ('formacao_informatica', '💻 Formação - Informática básica'),
            ('formacao_redes_sociais', '💻 Formação - Redes sociais'),
            ('formacao_workshops', '💻 Formação - Workshops temáticos'),
            ('formacao_apoio_estudo', '💻 Formação - Apoio ao estudo'),
            ('formacao_preparacao_exames', '💻 Formação - Preparação para exames'),
            ('formacao_linguas', '💻 Formação - Línguas estrangeiras'),
            ('formacao_capacitacao', '💻 Formação - Sessões de capacitação associativa'),
        ]
    )
    
    other_activities = StringField("Outras Atividades (especificar)", validators=[Length(max=200)])
    password = PasswordField("Password para Login da Associação", validators=[DataRequired()])
    submit = SubmitField("Guardar Associação")

class ActivityForm(FlaskForm):
    name = StringField("Nome da Atividade", validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField("Descrição da Atividade", validators=[DataRequired()])
    date = StringField("Data da Atividade (ex: 25/12/2024)", validators=[DataRequired(), Length(max=20)])
    location = StringField("Local da Atividade", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Guardar Atividade")

