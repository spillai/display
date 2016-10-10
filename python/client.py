import base64
import json
import numpy
import requests
import uuid
import cv2

from . import png

__all__ = ['URL', 'image', 'images', 'plot', 'send', 'text', 'set_port']

global URL
URL = 'http://localhost:8000/events'

def set_port(port=8000):
  global URL
  URL = 'http://localhost:{}/events'.format(port)

def uid():
  return 'pane_%s' % uuid.uuid4()

def send(**command):
  global URL
  command = json.dumps(command)
  headers = {'Content-Type' : 'application/text'}
  req = requests.post(URL, headers=headers, data=command.encode('ascii'))
  resp = req.content
  return resp is not None

def normalize(img, kwargs):
    minval = kwargs.get('min')
    if minval is None:
        minval = numpy.amin(img)
    maxval = kwargs.get('max')
    if maxval is None:
        maxval = numpy.amax(img)

    return numpy.uint8((img - minval) * (255/(maxval - minval)))


def to_rgb(img):
    nchannels = img.shape[2] if img.ndim == 3 else 1
    if nchannels == 3:
        return img
    if nchannels == 1:
        return img[:, :, numpy.newaxis].repeat(3, axis=2)
    raise ValueError('Image must be RGB or gray-scale')

def image(img, to_bgr=True, encoding='jpg', **kwargs):
    """ image(img, [win, title, labels, width])
    to_bgr: converts to bgr, if encoded as rgb (default True).
    encoding: 'jpg' (default) or 'png'
    """
    assert img.ndim == 2 or img.ndim == 3
    win = kwargs.get('win') or uid()

    if isinstance(img, list):
        return images(img, kwargs)
    # TODO: if img is a 3d tensor, then unstack it into a list of images

    img = to_rgb(normalize(img, kwargs))
    if to_bgr:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    #pngbytes = png.encode(img.tostring(), img.shape[1], img.shape[0])
    if encoding=='jpg':
        jpgbytes = cv2.imencode('.jpg', img)[1]
        imgdata = 'data:image/jpg;base64,' + base64.b64encode(jpgbytes).decode('ascii')
    elif encoding=='png':
        pngbytes = cv2.imencode('.png', img)[1]
        imgdata = 'data:image/png;base64,' + base64.b64encode(pngbytes).decode('ascii')
    else:
        raise ValueError('unknown encoding')

    send(command='image', id=win, src=imgdata,
        labels=kwargs.get('labels'),
        width=kwargs.get('width'),
        title=kwargs.get('title'))
    return win

def images(images, **kwargs):
    # TODO: need to merge images into a single canvas
    raise Exception('Not implemented')

def text(txt, **kwargs):
    win = kwargs.get('win') or uid()
    title = kwargs.get('title') or 'text'
    send(command='text', id=win, title=title, text=txt)

def plot(data, **kwargs):
    """ Plot data as line chart.
    Params:
        data: either a 2-d numpy array or a list of lists.
        win: pane id
        labels: list of series names, first series is always the X-axis
        see http://dygraphs.com/options.html for other supported options
    """
    win = kwargs.get('win') or uid()

    dataset = {}
    if type(data).__module__ == numpy.__name__:
        dataset = data.tolist()
    else:
        dataset = data

    # clone kwargs into options
    options = dict(kwargs)
    options['file'] = dataset
    if options.get('labels'):
        options['xlabel'] = options['labels'][0]

    # Don't pass our options to dygraphs.
    options.pop('win', None)

    send(command='plot', id=win, title=kwargs.get('title'), options=options)
    return win

