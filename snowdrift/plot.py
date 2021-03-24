from trollimage.image import Image as TImage
from trollimage.colormap import rdbu, Colormap
from PIL import ImageColor

# create trollimage scale def
def parseScaleDef(sdef):
    d = [] 
    for c in sdef:
        col = ImageColor.getcolor(c[1], "RGB")
        fCol = (col[0]/255.0, col[1]/255.0, col[2]/255.0)
        d.append((c[0], fCol))
    return d

ageScale = (
    (-1,'white'),
    (0, '#c0c0c0'),
    (1,'#808080'),
    (2,'#00f'),
    (4,'#0d0'),
    (8,'#ff0'),
    (16,'#f60'),
    (32,'#f00'),
    (64,'#f0f'),
    (128,'#808'),
)

ageCM = Colormap(*parseScaleDef(ageScale))


# Test plotter...
def plot(data):
    if 'snowage' in data:
        # plot snow age...
        vals = data['snowage']['values'][-1]

        img = TImage(vals, mode="L")
        img.palettize(ageCM)
        img.show()