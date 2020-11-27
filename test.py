from bokeh.plotting import figure, curdoc
from bokeh.palettes import Spectral4
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import (
    TextInput,
    Slider,
    Button,
    PreText,
    Div,
    Spinner,
    AbstractIcon,
)
from bokeh.layouts import column, row
from bokeh.document import Document
from bokeh.server.server import Server


def app(doc: Document):
    # updated chemreact1
    s1 = Slider(start=0, end=100, value=0, step=1)

    ti = TextInput()
    s = Spinner()
    b = Button(label="add")
    c = column(s1, s, b, ti)

    # c.apply_theme({"background-color": "red"})
    doc.add_root(c)


srv = Server(app)
srv.start()

if __name__ == "__main__":
    srv.io_loop.start()
