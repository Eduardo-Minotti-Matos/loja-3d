from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# ========================
# CONFIGURAÇÕES
# ========================

app.config['SECRET_KEY'] = 'chave_super_secreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Se estiver rodando no Render -> usa SQLite
if os.environ.get("RENDER") == "1":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
else:
    # Seu MySQL local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://edu:24102008@localhost/loja3d'

db = SQLAlchemy(app)


# ========================
# MODELOS
# ========================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)


class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)
    material = db.Column(db.String(50))
    cor = db.Column(db.String(50))


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float)


class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    quantidade = db.Column(db.Integer)
    preco_unitario = db.Column(db.Float)


# ========================
# ROTAS
# ========================

@app.route("/")
def index():
    produtos = Produto.query.all()
    return render_template("index.html", produtos=produtos)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])

        novo_usuario = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            return redirect(url_for("index"))
        else:
            return "Email ou senha inválidos"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ========================
# CRIAR TABELAS
# ========================

with app.app_context():
    db.create_all()

print("Banco configurado e tabelas criadas!")


if __name__ == "__main__":
    app.run(debug=True)