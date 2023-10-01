from PIL import Image

def calc_area(im: Image) -> float:
    '''
    Calculates the area of the shaded area in the image
    '''
    pixels = im.load()
    # count number of non-white pixels
    count, total = 0, 0
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if pixels[i, j] != (240, 240, 240):
                count += 1
            total += 1
    return float(100) * count / total

im = Image.open("test_img/1.png")
print(calc_area(im))