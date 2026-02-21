import math

def calcular_psnr(original_path, stego_path):
    _, pix_orig, w, h, rs = leer_bmp(original_path)
    _, pix_steg, _, _, _  = leer_bmp(stego_path)

    mse = sum((a - b)**2 for a, b in zip(pix_orig, pix_steg)) / (w * h * 3)

    if mse == 0:
        return float('inf')

    psnr = 10 * math.log10(255**2 / mse)

    print(f'MSE:  {mse:.6f}')
    print(f'PSNR: {psnr:.2f} dB  (>40 dB: cambio imperceptible)')

    return psnr


calcular_psnr('Images/hongo.bmp', 'hongo_500bytes.bmp')