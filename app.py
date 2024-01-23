from telebot import TeleBot
import google.generativeai as genai
import PIL.Image
from io import BytesIO

bot = TeleBot("")
genai.configure(api_key="")
model = genai.GenerativeModel('gemini-pro-vision')

@bot.message_handler(commands=['start'])
def handle_first_message(message):
      bot.send_message(message.chat.id, "Welcome to the image description bot! Please send me a photo to describe it.")


@bot.message_handler(content_types=['photo'])
def handle_image_message(message):
  # Send a loading message
  loading_message = bot.send_message(message.chat.id, "Processing the image, please wait...")

  global img

  try:
    image_file = bot.get_file(message.photo[-1].file_id)
    image_data = bot.download_file(image_file.file_path)
    img = PIL.Image.open(BytesIO(image_data))

    # Create Gemini Pro Vision request object
    response = model.generate_content(["Describe the photo.", img], stream=True)
    response.resolve()
    image_description = response.text

    # Send the image description as a response message
    bot.send_message(message.chat.id, f"{image_description}")

    bot.send_message(message.chat.id, "Do you have any more questions about the photo? Ask me anything!")
                
  except Exception as e:
    # Handle any errors that might occur during image processing
    bot.send_message(message.chat.id, f"Error processing the image: {str(e)}")

  finally:
    # Remove the loading message
    bot.delete_message(message.chat.id, loading_message.message_id)

@bot.message_handler(func=lambda message: True)  # Handle all text messages
def handle_text_message(message):
    global img
    loading_message = bot.send_message(message.chat.id, "Processing the image, please wait...")
    if img:  # Check if there's a recent image to reference
        # Create Gemini Pro Vision request object, incorporating stored image data
        response = model.generate_content([message.text, img], stream=True)
        response.resolve()
        answer = response.text

        # Send the answer
        bot.send_message(message.chat.id, f"{answer}")
    else:
        # Handle unrelated text messages (if needed)
        bot.send_message(message.chat.id, "I'm not sure how to respond to that. Please send me a photo for analysis.")

        # Remove the loading message
    bot.delete_message(message.chat.id, loading_message.message_id)

# Start polling
bot.polling()
