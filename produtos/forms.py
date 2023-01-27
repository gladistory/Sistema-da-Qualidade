from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import Form, IntegerField, StringField, BooleanField, TextAreaField, validators, DecimalField

class Addprodutos(Form):
    name = StringField('Nome do produto: ', [validators.DataRequired()])
    op = IntegerField('OP: ', [validators.DataRequired()])
    codigo = IntegerField('Código do Produto: ', [validators.DataRequired()])
    discription = TextAreaField('Descrição: ', [validators.DataRequired()])

class Addfiles(Form):
    name = StringField('Nome do Arquivo: ', [validators.DataRequired()])
    link = TextAreaField('Link Drive: ', [validators.DataRequired()])