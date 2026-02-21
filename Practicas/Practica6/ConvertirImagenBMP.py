from PIL import Image

img = Image.open('Images/pajaro.png')
img = img.resize((200,200))
img = img.convert('RGB')
img.save('pajaro.bmp')