import struct

# ====== (BLOQUE 1) Funciones tal como las tienes ======
def leer_bmp(filepath):
    '''Retorna (header_bytes, pixels, width, height, row_size)'''
    with open(filepath, 'rb') as f:
        data = f.read()

    offset = struct.unpack_from('<I', data, 10)[0]
    width  = struct.unpack_from('<i', data, 18)[0]
    height = struct.unpack_from('<i', data, 22)[0]
    row_size = (width * 3 + 3) & ~3
    header = bytearray(data[:offset])
    pixels = bytearray(data[offset:])
    return header, pixels, width, height, row_size


def guardar_bmp(filepath, header, pixels):
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixels)


def embed_lsb(src_path, dst_path, mensaje):
    header, pixels, width, height, row_size = leer_bmp(src_path)

    msg_bytes = mensaje.encode('utf-8')
    msg_len   = len(msg_bytes)

    # Convertir longitud (4 bytes) + mensaje a flujo de bits
    datos = struct.pack('>I', msg_len) + msg_bytes
    bits  = []

    for byte in datos:
        for i in range(7, -1, -1):         # MSB primero
            bits.append((byte >> i) & 1)

    # Verificar capacidad
    capacidad = (len(pixels) * 3) // 3 * 3   # múltiplos de 3 (B,G,R por píxel)
    # Simplificado: usar bytes secuenciales (saltando padding no es necesario aquí)

    if len(bits) > len(pixels):
        raise ValueError('Mensaje demasiado largo para esta imagen')

    # Incrustar bits en LSB de cada byte de canal
    pixels_mod = bytearray(pixels)

    for idx, bit in enumerate(bits):
        pixels_mod[idx] = (pixels_mod[idx] & 0xFE) | bit  # limpiar LSB e insertar bit

    guardar_bmp(dst_path, header, pixels_mod)
    print(f'[OK] Mensaje de {msg_len} bytes incrustado en {dst_path}')


def extract_lsb(stego_path):
    _, pixels, _, _, _ = leer_bmp(stego_path)

    # Leer primeros 32 bits → longitud del mensaje
    len_bits = [pixels[i] & 1 for i in range(32)]

    msg_len  = 0
    for b in len_bits:
        msg_len = (msg_len << 1) | b

    # Leer los siguientes msg_len*8 bits
    total_bits = 32 + msg_len * 8
    msg_bits   = [pixels[i] & 1 for i in range(32, total_bits)]

    # Reconstruir bytes
    msg_bytes = bytearray()

    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        msg_bytes.append(byte)

    return msg_bytes.decode('utf-8')


# ====== (BLOQUE 2) Calcular capacidad maxima real ======

# 1) Leer la imagen para conocer el tamaño real de pixels
_, pixels, w, h, rs = leer_bmp('Images/pajaro.bmp')

# 2) Calcular capacidad maxima segun TU logica
capacidad_max = (len(pixels) // 8) - 4

print("Bytes en pixels:", len(pixels))
print("Capacidad maxima (bytes):", capacidad_max)

# 3) Crear mensaje al limite exacto
mensaje = "A" * capacidad_max

print("Bytes del mensaje:", len(mensaje.encode('utf-8')))

# ====== Prueba (misma lógica, solo nombres consistentes) ======
embed_lsb('Images/pajaro.bmp', 'pajaro_capacidadmax.bmp', mensaje)
recuperado = extract_lsb('pajaro_capacidadmax.bmp')  # <- era 50000, por eso fallaba

print(f'Mensaje recuperado: {recuperado}')
assert recuperado == mensaje, '¡Error en la extracción!'
print('Prueba exitosa.')