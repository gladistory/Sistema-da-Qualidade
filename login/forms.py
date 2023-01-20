from wtforms import Form, BooleanField, StringField, PasswordField, validators  


class RegistrationForm(Form):
    name = StringField('Nome:', [validators.Length(min=4, max=25)])
    username = StringField('Usuário:', [validators.Length(min=4, max=25)])
    email = StringField('Email:', [validators.Length(min=6, max=35)])
    password = PasswordField('Nova senha:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Sua senha e confirmação não são as mesmas')
    ])
    confirm = PasswordField('Repetir senha:')

class LoginFormulario(Form):
     email = StringField('Email:', [validators.Length(min=6, max=35)])
     password = PasswordField('Senha:', [validators.DataRequired()])
