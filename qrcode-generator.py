#! /usr/bin/python
import pyqrcode
from xml.etree import ElementTree as et
import math
import sys
from wand.image import Image

# TODO: Encapsulate as callback for wx.Frame
def main(args1, args2, args3):
    block_size = 10
    circle_radius = block_size * 4

    def distance(p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def generateQRImageForUrl(url):
        qr_image = pyqrcode.MakeQRImage(url, errorCorrectLevel = pyqrcode.QRErrorCorrectLevel.H, block_in_pixels = 1, border_in_blocks=0)
	return qr_image

    def getSVGFileContent(filename):
    	document = et.parse(filename)
	root = document.getroot()
	for elem in root.iter("{http://www.w3.org/2000/svg}svg"):
		return elem

    def touchesBounds(center, x, y, radius, block_size):
	scaled_center = center / block_size
	dis = distance((scaled_center , scaled_center), (x, y))
	rad = radius / block_size
	return dis <= rad + 1	

    logoPath = args1
    url = args2
    output = args3
    outputname = output + '.svg'

    im = generateQRImageForUrl(url);

    imageSize = str(im.size[0] * block_size)

    # FIXME: Set the fit size
    # create an SVG XML element (see the SVG specification for attribute details)
    doc = et.Element('svg', width=imageSize, height=imageSize, version='1.1', xmlns='http://www.w3.org/2000/svg')

    pix = im.load()

    center = im.size[0] * block_size / 2

    for xPos in range(0,im.size[0]):
	for yPos in range(0, im.size[1]):

		color = pix[xPos, yPos]
		if color == (0,0,0,255):

			withinBounds = not touchesBounds(center, xPos, yPos, circle_radius, block_size)

			if (withinBounds):
				et.SubElement(doc, 'rect', x=str(xPos*block_size), y=str(yPos*block_size), width='10', height='10', fill='black')

    logo = getSVGFileContent(logoPath)

    test = str(logo.get("viewBox"))
    Array = []

    if (test != "None"):
        Array = test.split(" ")
        width = float(Array[2])
        height = float(Array[3])
    else :
        width = float(str(logo.get("width")).replace("px", ""))
        height = float(str(logo.get("height")).replace("px", ""))

    dim = height
    if (width > dim):
	dim = width
    scale = circle_radius * 2.0 / width

    scale_str = "scale(" + str(scale) + ")"

    xTrans = ((im.size[0] * block_size) - (width * scale)) / 2.0
    yTrans = ((im.size[1] * block_size) - (height * scale)) / 2.0

    translate = "translate(" + str(xTrans) + " " + str(yTrans) + ")"

    logo_scale_container = et.SubElement(doc, 'g', transform=translate + " " + scale_str)

    for element in logo.getchildren():
	logo_scale_container.append(element)

    # ElementTree 1.2 doesn't write the SVG file header errata, so do that manually
    f = open(outputname, 'w')
    f.write('<?xml version=\"1.0\" standalone=\"no\"?>\n')
    f.write('<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n')
    f.write('\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n')
    f.write(et.tostring(doc))
    f.close()

    # Convert the merged SVGs
    with Image(filename=outputname) as img:
        img.format = 'eps'
        img.save(filename=output + '.eps')
        print "EPS file saved as " + output + ".eps"

    with Image(filename=outputname) as img:
        img.format = 'ai'
        img.save(filename=output + '.ai')
        print "AI file saved as " + output + ".ai"

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Incorrect args, try:"
        print './generate.py <logo.svg> "<text>" <outfile>'
        sys.exit(0)

    main(sys.argv[1],sys.argv[2],sys.argv[3])
