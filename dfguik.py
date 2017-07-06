import kivy
kivy.require('1.10.0')
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.actionbar import ActionDropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.recycleview import RecycleView
from kivy.properties import BooleanProperty,\
                            ObjectProperty,\
                            NumericProperty,\
                            StringProperty

import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                   NavigationToolbar2Kivy
import matplotlib.pyplot as plt

from collections import OrderedDict
import numpy as np
import pandas as pd

import datetime
from datetime import date


Builder.load_string("""
<HeaderCell>
    size_hint: (None, None)
    text_size: self.size
    halign: "center"
    valign: "middle"
    height: '30dp'
    background_disabled_normal: '' 
    disabled_color: (1, 1, 1, 1)
    canvas.before:
        Color:
            rgba: 0.165, 0.165, 0.165, 1
        Rectangle:
            pos: self.pos
            size: self.size
    on_release: root.parent.parent.parent.parent._generate_table(self.text)

<TableHeader>:
    header: header
    bar_width: 0
    do_scroll: False
    size_hint: (1, None)
    effect_cls: "ScrollEffect"
    height: '30dp'
    GridLayout:
        id: header
        rows: 1
        size_hint: (None, None)
        width: self.minimum_width
        height: self.minimum_height

<ScrollCell>:
    canvas.before:
        Color:
            rgba: [0.23, 0.23, 0.23, 1] if root.is_even else [0.2, 0.2, 0.2, 1]
        Rectangle:
            pos: self.pos
            size: self.size
    text: root.text
    font_size: "12dp"
    halign: "center"
    valign: "middle"
    text_size: self.size
    size_hint: 1, 1
    height: 60
    width: 400

<TableData>:
    rgrid: rgrid
    scroll_type: ['bars', 'content']
    bar_color: [0.2, 0.7, 0.9, 1]
    bar_inactive_color: [0.2, 0.7, 0.9, .5]
    do_scroll_x: True
    do_scroll_y: True
    effect_cls: "ScrollEffect"
    viewclass: "ScrollCell"
    RecycleGridLayout:
        id: rgrid
        rows: root.nrows
        cols: root.ncols
        size_hint: (None, None)
        width: self.minimum_width
        height: self.minimum_height


<DfguiWidget>:
    panel1: data_frame_panel
    panel2: col_select_panel
    panel3: fil_select_panel
    panel4: hist_graph_panel
    panel5: scat_graph_panel

    do_default_tab: False

    TabbedPanelItem:
        text: 'Data Frame'
        on_release: root.open_panel1()
        DataframePanel:
            id: data_frame_panel
    TabbedPanelItem:
        text: 'Columns'
        ColumnSelectionPanel:
            id: col_select_panel
    TabbedPanelItem:
        text: 'Filters'
        FilterPanel:
            id: fil_select_panel
    TabbedPanelItem:
        text: 'Histogram'
        HistogramPlot:
            id: hist_graph_panel
    TabbedPanelItem:
        text: 'Scatter Plot'
        ScatterPlot:
            id: scat_graph_panel

<DataframePanel>:
    orientation: 'vertical'

<ColumnSelectionPanel>:
    col_list: col_list
    orientation: 'vertical'
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        size_hint: 1, 1
        scroll_timeout: 150
        GridLayout:
            id: col_list
            padding: "10sp"
            spacing: "5sp"
            cols:1
            row_default_height: '55dp'
            row_force_default: True
            size_hint_y: None

<FilterPanel>:
    filter_list: filter_list
    orientation: 'vertical'
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        size_hint: 1, 1
        scroll_timeout: 150
        GridLayout:
            id: filter_list
            padding: "10sp"
            spacing: "5sp"
            cols:1
            row_default_height: '55dp'
            row_force_default: True
            size_hint_y: None

<HistogramPlot>:
    select_btn: select_btn
    histogram: histogram
    orientation: 'vertical'
    Histogram:
        id: histogram
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        Button:
            id: select_btn
            text: 'Select Column'
            on_release: root.dropdown.open(self)
            size_hint_y: None
            height: '48dp'

<Histogram>:
    orientation: 'vertical'

<ScatterPlot>:
    select_btn1: select_btn1
    select_btn2: select_btn2
    scatter: scatter
    orientation: 'vertical'
    ScatterGraph:
        id: scatter
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        Button:
            id: select_btn1
            text: 'Select Column 1'
            on_release: root.dropdown1.open(self)
            size_hint_y: None
            height: '48dp'
        Button:
            id: select_btn2
            text: 'Select Column 2'
            on_release: root.dropdown2.open(self)
            size_hint_y: None
            height: '48dp'


<ScatterGraph>:
    orientation: 'vertical'


<ColDropDown>:
    #on_parent: self.dismiss()
    #on_select: btn.text = '{}'.format(args[1])
""")


''' Table Code from https://stackoverflow.com/questions/44463773/kivy-recycleview-recyclegridlayout-scrollable-label-problems#comment75948118_44463773
'''

class HeaderCell(Button):
    pass


class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, list_dicts=None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        titles = list_dicts[0].keys()

        for title in titles:
            self.header.add_widget(HeaderCell(text=title))


class ScrollCell(Label):
    text = StringProperty(None)
    is_even = BooleanProperty(None)


class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(list_dicts[0])

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            row_vals = ord_dict.values()
            for text in row_vals:
                self.data.append({'text': text, 'is_even': is_even})

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass
        
        
class Table(BoxLayout):

    def __init__(self, list_dicts=[], *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = TableHeader(list_dicts=list_dicts)
        self.table_data = TableData(list_dicts=list_dicts)

        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value


class DataframePanel(BoxLayout):
    """
    Panel providing the main data frame table view.
    """

    def populate_data(self, df):
        self.df_orig = df
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]
        self._disabled = []
        self.sort_key = None
        self._reset_mask()
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        df = self.get_filtered_df()
        data = []
        if disabled is not None:
            self._disabled = disabled
        keys = [x for x in df.columns[:] if x not in self._disabled]
        if sort_key is not None:
            self.sort_key = sort_key
        elif self.sort_key is None or self.sort_key in self._disabled:
            self.sort_key = keys[0]
        for i1 in range(len(df.iloc[:, 0])):
            row = OrderedDict.fromkeys(keys)
            for i2 in range(len(keys)):
                row[keys[i2]] = str(df.iloc[i1, i2])
            data.append(row)
        data = sorted(data, key=lambda k: k[self.sort_key]) 
        self.add_widget(Table(list_dicts=data))
        
    def apply_filter(self, conditions):
        """
        External interface to set a filter.
        """
        old_mask = self.mask.copy()

        if len(conditions) == 0:
            self._reset_mask()

        else:
            self._reset_mask()  # set all to True for destructive conjunction

            no_error = True
            for column, condition in conditions:
                if condition.strip() == '':
                    continue
                condition = condition.replace("_", "self.df_orig['{}']".format(column))
                print("Evaluating condition:", condition)
                try:
                    tmp_mask = eval(condition)
                    if isinstance(tmp_mask, pd.Series) and tmp_mask.dtype == np.bool:
                        self.mask &= tmp_mask
                except Exception as e:
                    print("Failed with:", e)
                    no_error = False

        has_changed = any(old_mask != self.mask)

    def get_filtered_df(self):
        return self.df_orig.loc[self.mask, :]

    def _reset_mask(self):
        pass
        self.mask = pd.Series([True] *
                              self.df_orig.shape[0],
                              index=self.df_orig.index)

    
class ColumnSelectionPanel(BoxLayout):
    """
    Panel for selecting and re-arranging columns.
    """

    def populate_columns(self, columns):
        """
        When DataFrame is initialized, fill the columns selection panel.
        """
        self.col_list.bind(minimum_height=self.col_list.setter('height'))
        for col in columns:
            self.col_list.add_widget(ToggleButton(text=col, state='down'))
    
    def get_disabled_columns(self):
        return [x.text for x in self.col_list.children if x.state != 'down']

    
class FilterPanel(BoxLayout):
    
    def populate(self, columns):            
        self.filter_list.bind(minimum_height=self.filter_list.setter('height'))
        for col in columns:
            self.filter_list.add_widget(FilterOption(columns))

    def get_filters(self):
        result=[]
        for opt_widget in self.filter_list.children:
            if opt_widget.is_option_set():
                result.append(opt_widget.get_filter())
        return [x.get_filter() for x in self.filter_list.children
                if x.is_option_set]
            
            
            
class FilterOption(BoxLayout):
        
    def __init__(self, columns, **kwargs):
        super(FilterOption, self).__init__(**kwargs)
        self.height="30sp"
        self.size_hint=(0.9, None)
        self.spacing=10
        options = ["Select Column"]
        options.extend(columns)
        self.spinner = Spinner(text='Select Column',
                               values= options,
                               size_hint=(0.25, None),
                               height="30sp",
                               pos_hint={'center_x': .5, 'center_y': .5})
        self.txt = TextInput(multiline=False, size_hint=(0.75, None),\
                             font_size="15sp")
        self.txt.bind(minimum_height=self.txt.setter('height'))
        self.add_widget(self.spinner)
        self.add_widget(self.txt)

    def is_option_set(self):
        return self.spinner.text != 'Select Column'

    def get_filter(self):
        return (self.spinner.text, self.txt.text)

            
class ColDropDown(DropDown):
    pass

    
class HistogramPlot(BoxLayout):
    """
    Panel providing a histogram plot.
    """
    
    def __init__(self, **kwargs):
        super(HistogramPlot, self).__init__(**kwargs)
        self.dropdown = ColDropDown()
        self.dropdown.bind(on_select=lambda instance, x:
                           setattr(self.select_btn, 'text', x))

    def populate_options(self, options):
        for index, option in enumerate(options):
            button = Button(text=option, size_hint=(1,None), height='48dp')
            button.bind(on_release=lambda x, y=index, z=option:
                        self.on_combo_box_select(y,z))
            self.dropdown.add_widget(button)
            
    
    def on_combo_box_select(self, index, text):
        self.dropdown.select(text)
        self.histogram.redraw(index)

    
class Histogram(BoxLayout):
    """
    Histogram portion of the histogram panel.
    """
    
    def __init__(self, **kwargs):
        super(Histogram, self).__init__(**kwargs)
        self.figure, self.axes = plt.subplots()
        self.add_widget(NavigationToolbar2Kivy(self.figure.canvas).actionbar)
        self.add_widget(self.figure.canvas)

    def redraw(self, selection):
        column_index1 = selection
        df = self.parent.parent.parent.df # TODO: Do this more elegantly.
        if column_index1 < len(df.iloc[:]) and column_index1 >= 0 and len(df) > 0:
            # NOTE: The following code generates a Type error  when attempting
            # to graph string data. The original code also generates this error,
            # but continues silently without alerting the user.
            self.axes.clear()
            try:
                self.axes.hist(np.array(df.iloc[:, column_index1].dropna().values), bins=100)
            except TypeError:
                self.warning("Invalid data type detected. Unable to generate graph.")
            except:
                self.warning("An unexpected error has occured.")
            finally:
                self.figure.canvas.draw()

    def warning(self, msg):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=msg,
                                    size_hint_y=1,
                                    text_size=(250,  None),
                                    halign='left',
                                    valign='middle'))
        button_layout = BoxLayout()
        close=Button(text="Close", size_hint=(0.8, 0.2))
        close.bind(on_release = lambda x : popup.dismiss())
        button_layout.add_widget(close)
        layout.add_widget(button_layout)
        popup = Popup(title='Histogram Error',
                      content=layout,
                      size_hint=(0.9, 0.9))
        popup.open()
            
class ScatterPlot(BoxLayout):
    """
    Panel providing a histogram plot.
    """
    
    def __init__(self, **kwargs):
        super(ScatterPlot, self).__init__(**kwargs)
        self.dropdown1 = ColDropDown()
        self.dropdown2 = ColDropDown()
        self.dropdown1.bind(on_select=lambda instance, x:
                           setattr(self.select_btn1, 'text', x))
        self.dropdown2.bind(on_select=lambda instance, x:
                           setattr(self.select_btn2, 'text', x))
        self.index1=-1
        self.index2=-1

    def populate_options(self, options):
        for index, option in enumerate(options):
            button = Button(text=option, size_hint=(1,None), height='48dp')
            button.bind(on_release=lambda x, y=index, z=option:
                        self.on_combo_box_select1(y,z))
            self.dropdown1.add_widget(button)
        for index, option in enumerate(options):
            button = Button(text=option, size_hint=(1,None), height='48dp')
            button.bind(on_release=lambda x, y=index, z=option:
                        self.on_combo_box_select2(y,z))
            self.dropdown2.add_widget(button)
            
    def on_combo_box_select1(self, index, text):
        self.dropdown1.select(text)
        self.index1 = index
        if self.index1 >=0 and self.index2 >= 0:
            self.scatter.redraw(self.index1, self.index2)

    def on_combo_box_select2(self, index, text):
        self.dropdown2.select(text)
        self.index2 = index
        if self.index1 >=0 and self.index2 >= 0:
            self.scatter.redraw(self.index1, self.index2)

    
class ScatterGraph(BoxLayout):
    """
    Histogram portion of the histogram panel.
    """
    
    def __init__(self, **kwargs):
        super(ScatterGraph, self).__init__(**kwargs)
        self.figure, self.axes = plt.subplots()
        self.add_widget(NavigationToolbar2Kivy(self.figure.canvas).actionbar)
        self.add_widget(self.figure.canvas)

    def redraw(self, selection1, selection2):
        column_index1 = selection1
        column_index2 = selection2
        df = self.parent.parent.parent.df # TODO: Do this more elegantly.
        if column_index1 < len(df.iloc[:]) and\
           column_index1 >= 0 and\
           column_index2 < len(df.iloc[:]) and\
           column_index2 >= 0 and len(df) > 0:
            # NOTE: The following code generates a Type error  when attempting
            # to graph string data. The original code also generates this
            # error, but continues silently without alerting the user.
            self.axes.clear()
            try:
                self.axes.plot(df.iloc[:, column_index1].values,
                               df.iloc[:, column_index2].values,
                               'o', clip_on=False)
            except TypeError:
                self.warning("Invalid data type detected. Unable to generate graph.")
            except:
                self.warning("An unexpected error has occured.")
            finally:
                self.figure.canvas.draw()

    def warning(self, msg):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=msg,
                                    size_hint_y=1,
                                    text_size=(250,  None),
                                    halign='left',
                                    valign='middle'))
        button_layout = BoxLayout()
        close=Button(text="Close", size_hint=(0.8, 0.2))
        close.bind(on_release = lambda x : popup.dismiss())
        button_layout.add_widget(close)
        layout.add_widget(button_layout)
        popup = Popup(title='Histogram Error',
                      content=layout,
                      size_hint=(0.9, 0.9))
        popup.open()

class DfguiWidget(TabbedPanel):

    def __init__(self, df, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.panel1.populate_data(df)
        self.panel2.populate_columns(df.columns[:])
        self.panel3.populate(df.columns[:])
        self.panel4.populate_options(df.columns[:])
        self.panel5.populate_options(df.columns[:])

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        #arr = self.panel3.get_filters()
        #print(str(arr))
        self.panel1.apply_filter(self.panel3.get_filters())
        self.panel1._generate_table(disabled=
                                    self.panel2.get_disabled_columns())

        
