from time import sleep
from webbrowser import open_new_tab
from xml.etree.ElementTree import Element as eElement, tostring


class Element:
    def __init__(self, name, **kw):
        kw = {k.replace('_','-'): str(v) for k, v in kw.items()}
        self.element = eElement(name, **kw)

    def add(self, e, **k):
        if not isinstance(e, Element):
            e = Element(e, **k)
        self.element.append(e.element)
        return e

    def __setattr__(self, name, value):
        if name == 'element':
            object.__setattr__(self, name, value)
        else:
            setattr(self.element, name, value)

    def __str__(self):
        return tostring(self.element).decode()


class SVG:
    '''
        https://www.w3schools.com/tags/tag_svg.asp
        https://developer.mozilla.org/fr/docs/Web/SVG/Element/svg
    '''
    def __init__(self, **k):
        debug = k.pop('debug', False)
        k['xmlns'] = 'http://www.w3.org/2000/svg'
        k['version'] = '1.1'
        width = k.setdefault('width', 800)
        height = k.setdefault('height', 600)
        k.setdefault('viewBox', f'0 0 {width} {height}'),
        if 0 and debug: # __to__chk__:
            k.setdefault('style', 'border:10 solid red')
        self.root = Element('svg', **k)
        self.add = self.root.add
        if debug:
            self.add('rect',
                width = width,
                height = height,
                fill = 'rgb(222, 222, 222)',
            )
        self.width = width
        self.height = height

    def save_svg(self, path):
        with open(path, 'w') as f:
            f.write('<?xml version=\"1.0\" standalone=\"no\"?>\n')
            f.write('<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n')
            f.write('\"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n')
            f.write(str(self))

    def save_html(self, path):
        with open(path, 'w') as f:
            f.write('<html><body>')
            f.write(str(self))
            f.write('</body><html>')

    def save(self, path):
        if path.endswith('svg'):
            self.save_svg(path)
        elif path.endswith('html'):
            self.save_html(path)
        else:
            raise ValueError(f'Invalid path : {path}')

    def open(self):
        path = '/tmp/pybrary_svg.html'
        self.save(path)
        open_new_tab(path)
        sleep(1)

    def __str__(self):
        return f'{self.root}'
