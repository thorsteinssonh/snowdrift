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

defaultScale = (
    (0,'black'),
    (1,'white')
)

snowageScale = (
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

driftaccScale = (
    (0,'white'),
    (0.5, '#808080'),
    (1, '#0cf'),
    (2, '#0ff'),
    (4, '#0f0'),
    (8, '#ff0'),
    (12, '#fc0'),
    (24, '#f0f')
)

mobilityScale = (
    (0,'white'),
    (0.3, '#dd0'),
    (0.6, '#00be80'),
    (1, '#0000d0'),
)

driftScale = (
    (0,'#0d0'),
    (0.09, '#0dd'),
    (0.2, '#dd0'),
    (0.5, '#d00'),
)

def getCM(param, vals):
    if param == 'snowage':
        return Colormap(*parseScaleDef(snowageScale))
    elif param == 'driftacc':
        return Colormap(*parseScaleDef(driftaccScale))
    elif param == 'mobility':
        return Colormap(*parseScaleDef(mobilityScale))
    elif param == 'drift':
        return Colormap(*parseScaleDef(driftScale))
    else:
        cm = Colormap(*parseScaleDef(defaultScale))
        cm.set_range(vals.min(), vals.max())
        return cm


# Test plotter...
def plot(data, i, param):

    # plot snow age...
    vals = data[param]['values'][i][::-1,:]

    img = TImage(vals, mode="L")

    cm = getCM(param, vals)
    img.palettize(cm)
    #img.colorize(cm)
    img.show()