from itertools import cycle
import json
import chemreact
import os

from bokeh.plotting import figure, curdoc
from bokeh.palettes import Spectral4
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import TextInput, Slider, Button, PreText, Div, Spinner
from bokeh.layouts import column, row, layout

chem = chemreact.models.Chemistry()
chem.solver_params(method="RK45")
doc = curdoc()


def add_reaction(reaction: str, kf=0.5, kr=0.5):
    txt = PreText(text=reaction)
    if "<=>" in reaction:
        chem.reaction(reaction, k1=kf, k2=kr)
        sl_kf = Slider(
            start=0,
            end=1,
            value=kf,
            step=0.01,
            title="kf",
            name=str(len(chem.rate_constants) - 2),
            max_width=250,
        )
        sl_kr = Slider(
            start=0,
            end=1,
            value=kr,
            step=0.01,
            title="kr",
            name=str(len(chem.rate_constants) - 1),
            max_width=250,
        )
        row_reaction = layout([txt, [sl_kf], [sl_kr]])
        sl_kf.on_change("value", lambda a, o, n: run(k=n, ind=sl_kf.name))
        sl_kr.on_change("value", lambda a, o, n: run(k=n, ind=sl_kr.name))
    elif "=>" in reaction:
        chem.reaction(reaction, k=kf)
        sl_kf = Slider(
            start=0,
            end=1,
            value=kf,
            step=0.01,
            title="kf",
            name=str(len(chem.rate_constants) - 1),
            max_width=250,
        )
        bt_up = Button()
        bt_dw = Button()
        row_reaction = row(txt, sl_kf)
        sl_kf.on_change("value", lambda a, o, n: run(k=sl_kf.value, ind=sl_kf.name))
    col.children.append(row_reaction)

    existing_species = [i.name for i in col_species.children]
    new_species = [i for i in chem.variables if i not in existing_species]
    for i in new_species:
        col_species.children.append(get_new_species(i))
    run(new_spec=new_species)


def get_new_species(species):
    sp_ns = Spinner(title=species, value=0, low=0, step=0.1, name=species, max_width=50)
    sp_ns.on_change("value", lambda a, o, n: run(init_conc={species: float(n)}))
    return sp_ns


def run(k=None, ind=None, init_conc=None, new_spec=None):
    doc.hold(policy="combine")
    if init_conc != None:
        chem.initial_concentrations(**init_conc)
    if k != None or ind != None:
        chem.rate_constants[int(ind)] = float(k)
    chem.run(plot=False)
    source.data = chem.solution
    if new_spec != None:
        for i in new_spec:
            plot.line(
                x="t", y=i, source=source, legend_label=i, color=next(iter_colors)
            )
        plot.legend.location = "top_right"
        plot.legend.click_policy = "hide"
    doc.unhold()


ti = TextInput(title="enter reaction", value="A=>B", max_width=200)
ti.on_change("value", lambda a, o, n: add_reaction(n))
bt_add = Button(label="add", align="end", width=100)
bt_add.on_click(lambda: add_reaction(ti.value))
row_inp = row(ti, bt_add)
# row_inp.apply_theme({"left": 1000})
col = column()
col_species = column()
source = ColumnDataSource()
plot = figure(sizing_mode="stretch_both", max_height=300, min_height=200, max_width=600)
iter_colors = cycle(Spectral4)
curdoc().add_root(
    layout(
        [[plot], [row_inp], [col, col_species]],
        sizing_mode="stretch_both",
        max_width=600,
    )
)


def setup(app_type):
    with open("kinetics/Data/reactions.json") as f:
        data = json.load(f)
    if app_type not in data.keys():
        return

    data = data[app_type]
    ti.value = ""
    for r in data["reactions"]:
        add_reaction(r)

    # Warning: works only for irreversible reactions:
    for i, k in zip(col.children, data["rate_const"]):
        i.children[1].value = k

    for i in col_species.children:
        if i.name in data["initial_cond"].keys():
            i.value = data["initial_cond"][i.name]


# HTTP request handler to pre-set the app:
args = curdoc().session_context.request.arguments
try:
    app_type = args.get("type")[0].decode("utf-8")
    setup(app_type)
except:
    app_type = 200

try:
    if os.environ["BOKEH_VS_DEBUG"] == "true":
        import ptvsd

        # 5678 is the default attach port in the VS Code debug configurations
        print("Waiting for debugger attach")
        ptvsd.enable_attach(address=("localhost", 5678), redirect_output=True)
        ptvsd.wait_for_attach()
except:
    pass
