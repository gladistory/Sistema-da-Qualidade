from unicodedata import name
from flask import Flask, render_template, request, redirect, flash, session,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from login.forms import RegistrationForm, LoginFormulario
from datetime import datetime
from produtos.forms import Addprodutos
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plasc.db'
app.config['SECRET_KEY']='çuizsbregkjbewui1234'
app.config['UPLOAD_FOLDER'] = 'static/files'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), unique=False, nullable=False)
    profile = db.Column(db.String(80), unique=False, nullable=False, default='profile.jpg')


    def __repr__(self):
        return '<User %r>' % self.username

class Addproduto(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    op=db.Column(db.Integer, nullable=False)
    codigo=db.Column(db.Integer, nullable=False)
    discription=db.Column(db.Text, nullable=False)
    pub_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    marca_id=db.Column(db.Integer, db.ForeignKey('marca.id'), nullable=False)
    marca=db.relationship('Marca', backref=db.backref('marcas', lazy=True))

    categoria_id=db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    categoria=db.relationship('Categoria', backref=db.backref('categorias', lazy=True))

    def __repr__(self):
        return '<Addproduto %r>' % self.name

class Marca(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(30), nullable=False, unique=True)


class Categoria(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(30), nullable=False, unique=True)
    
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        flash(f'Upload feito com sucesso', 'success')
        return redirect(request.args.get('next') or url_for('admin'))
    return render_template('admin/upload.html', form=form)


@app.route('/')
@app.route("/home")
def home():
    return render_template('client/home.html', title='Sistema de Qualidade Plasc')

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))
    produtos = Addproduto.query.all()
    return render_template('admin/index.html', title='Página do Administrador',  produtos=produtos)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, username=form.username.data , email=form.email.data,
        password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Obrigado {form.name.data} pelo seu registro', 'success')
        return redirect(url_for('login'))
    return render_template('admin/registrar.html', form=form, title="Página de Registro")


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginFormulario(request.form)
    if request.method =="POST" and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Olá {form.email.data}, Você acessou seu perfil', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
                flash(f'Não foi possível acessar sua conta. Verifique se os dados estão corretos.', 'danger')    
    return render_template('admin/login.html', form=form, title='Login')


@app.route('/marcas')
def marcas():
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))
    marcas = Marca.query.order_by(Marca.id.desc()).all()
    return render_template('admin/marca.html', title='Página Marcas', marcas=marcas)

@app.route('/categoria')
def categoria():
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))
    categorias = Categoria.query.order_by(Categoria.id.desc()).all()
    return render_template('admin/marca.html', title='Página Categorias', categorias=categorias)

@app.route('/addmarca', methods=['GET', 'POST'])
def addmarca():

    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))

    if request.method=="POST":
        getmarca = request.form.get('marca')
        marca = Marca(name=getmarca)
        db.session.add(marca)
        flash(f'A marca {getmarca} foi cadastrada com sucesso', 'success')
        db.session.commit()
        return redirect(url_for('addmarca'))
    return render_template('/produtos/addmarca.html', marcas='marcas', title='Adicionar Fabricante')

@app.route('/updatemarca/<int:id>', methods=['GET', 'POST'])
def updatemarca(id):
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))
    updatemarca = Marca.query.get_or_404(id)
    marca = request.form.get('marca')
    if request.method=='POST':
        updatemarca.name = marca
        db.session.commit()
        flash(f'Seu Fabricante foi atualizado com sucesso!', 'success')
        return redirect(url_for('marcas'))
    return render_template('/produtos/updatemarca.html', title='Atualizar Produto', updatemarca='updatemarca' )

@app.route('/deletemarca/<int:id>', methods=['GET', 'POST'])
def deletemarca(id):
    marca = Marca.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(marca)
        db.session.commit()
        flash(f'Sua MARCA {marca.name} FOI DELETADA com sucesso!', 'success')
        return redirect(url_for('marcas'))
    flash(f'Sua MARCA {marca.name} NÂO FOI DELETADA', 'warning')
    return redirect(url_for('marcas'))

@app.route('/addcat', methods=['GET', 'POST'])
def addcat():
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))

    if request.method=="POST":
        getmarca = request.form.get('categoria')
        cat = Categoria(name=getmarca)
        db.session.add(cat)
        flash(f'A Categoria {getmarca} foi cadastrada com sucesso', 'success')
        db.session.commit()

        return redirect(url_for('addcat'))
    return render_template('/produtos/addmarca.html', title='Adicionar Categoria')

@app.route('/updatecat/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))
    updatecat = Categoria.query.get_or_404(id)
    categoria = request.form.get('categoria')
    if request.method=='POST':
        updatecat.name = categoria
        flash(f'Sua categoria foi atualizado com sucesso!', 'success')
        db.session.commit()
        return redirect(url_for('categoria'))
    return render_template('/produtos/updatemarca.html', title='Atualizar Categoria', updatecat='updatecat' )

@app.route('/deletecat/<int:id>', methods=['GET', 'POST'])
def deletecat(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(categoria)
        db.session.commit()
        flash(f'Sua MARCA {categoria.name} FOI DELETADA com sucesso!', 'success')
        return redirect(url_for('admin'))
    flash(f'Sua MARCA {categoria.name} NÂO FOI DELETADA', 'warning')
    return redirect(url_for('admin'))

@app.route('/addproduto', methods=['GET', 'POST'])
def addproduto():
    if 'email' not in session:
        flash(f'Por favor, é necessario que faça seu login no sistema', 'danger')
        return redirect(url_for('login'))

    marcas = Marca.query.all()
    categorias = Categoria.query.all()
    form = Addprodutos(request.form)

    if request.method=="POST":
        name = form.name.data
        op = form.op.data
        codigo = form.codigo.data
        discription = form.discription.data
        marca = request.form.get('marca')
        categoria = request.form.get('categoria')

        addpro = Addproduto(marca_id=marca, categoria_id=categoria, name=name, op=op, codigo=codigo, discription=discription)
        db.session.add(addpro)
        flash(f'O produto {name} foi cadastrado com sucesso', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('/produtos/addprodutos.html', title="Cadastrar Produtos", form=form, marcas=marcas, categorias=categorias)
    
@app.route('/updateproduto/<int:id>', methods=['GET', 'POST'])
def updateproduto(id):
    marcas = Marca.query.all()
    categorias = Categoria.query.all()
    produto = Addproduto.query.get_or_404(id)
    marca = request.form.get('marca')
    categoria = request.form.get('categoria')
    form = Addprodutos(request.form)
    if request.method=="POST":
        produto.name = form.name.data
        produto.op = form.op.data
        produto.discription = form.discription.data
        produto.codigo = form.codigo.data
        produto.marca_id = marca
        produto.categoria_id = categoria


        db.session.commit()
        flash(f'O produto foi Atualizado com sucesso', 'success')
        return redirect('/admin')

    
    form.name.data = produto.name
    form.discription.data = produto.discription
    form.op.data = produto.op
    form.codigo.data = produto.codigo
    
    return render_template('/produtos/updateproduto.html', title='Atualizar Produtos',form=form, marcas=marcas, produto=produto, categorias=categorias)

@app.route('/deleteproduto/<int:id>', methods=['POST'])
def deleteproduto(id):
    produto = Addproduto.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(produto)
        db.session.commit()
        flash(f'Seu Produto {produto.name} FOI DELETADA com sucesso!', 'success')
        return redirect(url_for('admin'))
    flash(f'Seu Produto {produto.name} NÃO FOI DELETADA !', 'warning')
    return redirect(url_for('admin')) 



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
