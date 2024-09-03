import sys
import copy
import math
import getopt
from PIL import Image


def get_pixel(img, x, y):
    """Returns the value of a pixel"""
    width = img.width
    height = img.height
    x_ = min(width-1, max(0, x))
    y_ = min(height-1, max(0, y))
    return img.getpixel((x_, y_))


def is_picture(img, x, y):
    """ Checks if the pixel at (x, y) is part of a picture or the background"""
    pixel = [(255,255,255, 255) for i in range(5)]
    pixel[0] = get_pixel(img, x, y)
    pixel[1] = get_pixel(img, x, y-1)
    pixel[2] = get_pixel(img, x, y+1)
    pixel[3] = get_pixel(img, x+1, y)
    pixel[4] = get_pixel(img, x-1, y)
    val = sum([sum(p)//len(p) for p in pixel])//len(pixel)
    if thld_bg < 255-val:
        return True
    else:
        return False


def in_box(boxes, x, y):
    """Finds out whether a pixel is inside one of the boxes listed"""
    for box in boxes:
        x1, y1, x2, y2 = box
        if x>=x1 and x<=x2 and y>=y1 and y<=y2:
            return True
    return False


def boxes_intersect(boxes, box):
    """Determine whether a box intersects with any of the boxes listed"""
    x1, y1, x2, y2 = box
    if in_box(boxes, x1, y1) \
        or in_box(boxes, x1, y2) \
        or in_box(boxes, x2, y1) \
        or in_box(boxes, x2, y2):
        return True
    return False


def area(box):
    """Returns the area of a box"""
    x1, y1, x2, y2 = box
    return (x2-x1)*(y2-y1)


def extract_image(boxes_exclude, img, x, y):
    """Returns the area that may contain a picture"""
    width = img.width
    height = img.height

    x1 = x
    while x<width-1 and is_picture(img, x, y) \
            and not in_box(boxes_exclude, x, y):
        x += 1
    x2 = x

    x = x1+(x2-x1)*pos_x
    y0 = y
    while y>0 and is_picture(img, x, y) \
          and not boxes_intersect(boxes_exclude, (x1, y, x2, y)):
        y -= 1
    y1 = y

    y = y0
    while y<height-1 and is_picture(img, x, y) \
          and not boxes_intersect(boxes_exclude, (x1, y1, x2, y)):
        y += 1
    y2 = y

    y = y1+(y2-y1)*pos_y
    x = x2
    while x<width-1 and is_picture(img, x, y) \
          and not boxes_intersect(boxes_exclude, (x1,y1,x,y2)):
        x += 1
    x2 = x

    x = x1
    while x>0 and is_picture(img, x, y) \
          and not boxes_intersect(boxes_exclude, (x,y1,x2,y2)):
        x -= 1
    x1 = x

    if x2-x1>min_len and y2-y1>min_len:
        return (x1, y1, x2, y2)
    else:
        return None


def trim_edge(img, box, axis, side):
    """Returns the position where the box can be moved"""
    x1, y1, x2, y2 = box
    if axis == 0:
        if side == 0:
            domain_y = range(y1, y2)
        else:
            domain_y = reversed(range(y1, y2))
        score = 0
        for y in domain_y:
            for x in range(x1, x2):
                score += is_picture(img, x, y)
            score /= (x2-x1)
            if score > conf_lvl:
                return y
        return y1 if side==0 else y2
    else:
        if side == 0:
            domain_x = range(x1, x2)
        else:
            domain_x = reversed(range(x1, x2))
        score = 0
        for x in domain_x:
            for y in range(y1, y2):
                score += is_picture(img, x, y)
            score /= (y2-y1)
            if score > conf_lvl:
                return x
        return x1 if side==0 else x2


def crop_img(img, box):
    """Removes white spaces from the borders"""
    y1 = trim_edge(img, box, 0, 0)
    y2 = trim_edge(img, box, 0, 1)
    x1 = trim_edge(img, box, 1, 0)
    x2 = trim_edge(img, box, 1, 1)
    return (x1, y1, x2, y2)


img_name = ''
freq = 0.05
min_area = 0.1
thld_bg = 6
min_entropy = 0.8
pos_x = 0.5
pos_y = 0.5
conf_lvl = 0.6
min_len = 100

options = ['freq=', 'min_len=', 'min_area=', 'min_entropy=', 'pos_x=', 'pos_y=', 'conf_lvl=']
try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:f:", options)
except getopt.GetoptError:
    print('python extract.py -i <input image>')
    sys.exit()

for opt, arg in opts:
    if opt == '-h':
        print('python extract.py -i <input image>')
        print('Options:')
        print('-i \t\t Name of the input image')
        print('-f, --freq')
        print(' \t\t Percentage of the pixels scanned. Default {}'.format(freq))
        print('--min_len')
        print(' \t\t Subimages have a minimum length on each axis. Default {}'.format(min_len))
        print('--min_area')
        print(' \t\t Subimages have a fraction of the original area . Default {}'.format(min_area))
        print('--min_entropy')
        print(' \t\t Subimages have a fraction of the original entropy . Default {}'.format(min_entropy))
        print('--pos_x')
        print(' \t\t Position in the x axis to find the height of the picture. Default {}'.format(pos_x))
        print('--pos_y')
        print(' \t\t Position in the y axis to find the width of the picture. Default {}'.format(pos_y))
        print('--conf_lvl')
        print(' \t\t Confidence level to distinguish an image from the background. Default {}'.format(conf_lvl))
        print('--thld_bg')
        print(" \t\t Threshold to distinguish a photo's  pixel from the background. Default {}".format(thld_bg))
        sys.exit()
    elif opt == '-i':
        img_name = arg
    elif opt in ['-f', '--freq']:
        freq = float(arg)
    elif opt == '--min_area':
        min_area = float(arg)
    elif opt == '--min_len':
        min_len = float(arg)
    elif opt == '--min_entropy':
        min_entropy = float(arg)
    elif opt == '--pos_x':
        pos_x = float(arg)
    elif opt == '--pos_y':
        pos_y = float(arg)
    elif opt == '--conf_lvl':
        conf_lvl = float(arg)


if img_name == '':
    print('No input file')
    sys.exit()


img = Image.open(img_name)
width = img.width
height = img.height

extension = img_name[-4:]
step = int(1/freq)

boxes_exclude = []
img_num = 0
for y in range(step, height, step):
    for x in range(step, width, step):
        if not in_box(boxes_exclude, x, y) and is_picture(img, x, y):
            box_img = extract_image(boxes_exclude, img, x, y)
            if box_img != None:
                box_img_b = crop_img(img, box_img)
                if area(box_img_b) > area(box_img)*min_area:
                    box_img = box_img_b
                new_img = img.crop(box=box_img)
                if new_img.entropy() > img.entropy()*min_entropy:
                    new_img.save(img_name[:-4] + '_' + str(img_num) + extension)
                    boxes_exclude.append( box_img )
                    img_num += 1


def main():
    pass