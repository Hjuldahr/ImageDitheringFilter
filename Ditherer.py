import os
from PIL import Image

def read_bayer_csv_file(file_name):
    with open(f'Art\\conf\\{file_name}.csv') as f:
        return tuple(
            tuple(
                map(int, line.split(','))
            ) for line in f
        )
        
def read_palette_hex_file(file_name):
    with open(f'Art\\conf\\{file_name}.hex') as f:
        return tuple(hex_to_rgb(line) for line in f)

def rgb_to_hex(rgb):
    return (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]

def hex_to_rgb(hexcode):
    hexcode = int(hexcode.rstrip(), base=16)
    return ((hexcode >> 16), (hexcode >> 8) & 0xFF, hexcode & 0xFF)

def calculate_rgb_brightness(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

def rgb_distance(rgb1, rgb2):
    #https://en.wikipedia.org/wiki/Color_difference (redmean)
    
    delta_r_sqr = (rgb1[0] - rgb2[0]) ** 2
    delta_g_sqr = (rgb1[1] - rgb2[1]) ** 2
    delta_b_sqr = (rgb1[2] - rgb2[2]) ** 2
    
    red_mean = (rgb1[0] + rgb2[0]) / 2
    
    return (2 + red_mean / 256) * delta_r_sqr + 4 * delta_g_sqr + (2 + (255 - red_mean) / 256) * delta_b_sqr

def find_closest_palette(rgb, palette_hex):
    min_dist = float('inf')
    best_fit = (0, 0, 0)
    for p in palette_hex:
        dist = rgb_distance(p, rgb)
        if dist < min_dist:
            min_dist = dist
            best_fit = p

    return best_fit

def can_dither(x, y, brightness, bayer, bayerWidth, bayerHeight):
    return ((brightness / 255) * bayerWidth * bayerHeight) > bayer[y % bayerHeight][x % bayerWidth]

def process_image(oldImage, bayer, palette):
    bayerWidth = len(bayer[0])
    bayerHeight = len(bayer)
    darkest = find_closest_palette((0, 0, 0), palette)
    
    oldPixels = oldImage.load()
    size = oldImage.size
    newImage = Image.new('RGB', oldImage.size, darkest)
    newPixels = newImage.load()
    
    for y in range(size[1]):
        for x in range(size[0]):
            rgb = oldPixels[x, y]
            if can_dither(x, y, calculate_rgb_brightness(rgb), bayer, bayerWidth, bayerHeight):
                newPixels[x, y] = find_closest_palette(rgb, palette)
                
    return newImage

if __name__ == '__main__':
    os.makedirs('Art\\conf', exist_ok=True)
    os.makedirs('Art\\Generated Images', exist_ok=True)
    
    sourceFile = 'artworks-JPoVuXDmFWCLhyVS-oysneg-t1080x1080.jpg'
    sourceFileName, sourceFileType = sourceFile.split('.')
    
    bayerFileName = 'bayer_4x4'
    
    paletteFileName = 'apollo'
    
    newFile = f'{sourceFileName}-{bayerFileName}-{paletteFileName}.{sourceFileType}'
    
    print(f'Reading Bayer File: {bayerFileName}.csv')
    bayer = read_bayer_csv_file(bayerFileName)
    
    print(f'Reading Palette File: {paletteFileName}.hex')
    palette = read_palette_hex_file(paletteFileName)
    
    print(f'Reading Source File: {sourceFile}')
    image = Image.open(f'Art\\Source Images\\{sourceFile}', mode='r').convert('RGB')
    
    print('Processing')
    newImage = process_image(image, bayer, palette)
    
    print(f'Writing Output File: {newFile}')
    
    newImage.save(f'Art\\Generated Images\\{newFile}')
    newImage.show()