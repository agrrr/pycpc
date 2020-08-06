import matplotlib.pyplot as plt
from htmlcreator import HTMLDocument
import mpld3
from pathlib import Path
import uuid
import webbrowser
import pandas as pd
from logs_util import ProjectPaths

class HTML_Report:
    def __init__(self, name, title=None):
        self.name = name
        self.document = HTMLDocument()
        self.document.set_title(title if title is not None else name)
        self.footer = ''
        self.document.style = ( \
"""

body {
    max-width: 1060px;
    margin: auto;
    padding-bottom: 20px;
    font-family: "Lato", sans-serif;
}
p{
    font-family: sans-serif;
    overflow-x: hidden;
    color: var(--gray90);
    font-family: "Lato", sans-serif;
    font-size: 1.5rem;
    line-height: 1.5rem; 
    font-size:16px;
    text-indent: 0;
    text-align: left
}
div.pandas-dataframe {
    overflow: auto;
}
table.dataframe {
    border-collapse: collapse;
    border: none;
}
table.dataframe td {
  background-color: #fffef4;
  font-size: 14px;
  text-align: center;
  white-space: nowrap;
  margin: 0;
  padding-top: 0.4em;
  padding-bottom: 0.4em;
  padding-left: 0.5em;
  padding-right: 0.5em;
  border: 1px solid #d7d7d7;
}
table.dataframe th {
  background-color: #f9f9f9;
  font-size: 12px;
  text-align: center;
  white-space: nowrap;
  padding-left: 1em;
  padding-right: 1em;
  padding-top: 0.5em;
  padding-bottom: 0.5em;
  border: 1px solid #e0e0e0;
}
table.dataframe tr:nth-child(even) td {
  background: #fff2e4;
}
table.dataframe tr:nth-child(odd) td {
  background: #ffffe8;
}
table.dataframe tr:hover td {
  background-color: #ddeeff;
}
table.dataframe tbody th {
  font-weight: normal;
}

h4{
  background-color: #F8F7F7
}
h3{
  background-color: #FDF2E9
}
h2{
  background-color: #FAE5D3 
}
h1{
  background-color: #FDF2E9
}
""")

    def add_header(self, header, level: int = 1):
        self.document.add_header(header, level=f'h{level}', align='center')
        print('##' + '>>' * (5-level) + ' ' + header + ' ' + (5-level) * '<<' + '##')

    def add_text(self, text):
        self.document.add_text(text)  # defaults: size='16px', indent='0' alight='left'

    def add_html(self, text):
        self.document.body += text
        
    def add_line_break(self):
        self.document.add_line_break()

    def add_fig(self, fig, close=True):
        self.document.body += mpld3.fig_to_html(fig)
        if close:
          plt.close(fig)
    def add_df(self, df):
        self.document.add_table(df)
    
    def add_dict(self, dic):
        self.add_df(pd.Series(dic).to_frame().T)

    def add_img(self, image_url, title='', width_percent=100):
        self.document.add_image_link(image_url, title=title, width=f'{width_percent}%')

    def save(self, open=True):
        htmlfile = ProjectPaths.html_dir / f'{self.name} {uuid.uuid1()}.html'
        self.document.add_text(self.footer)
        self.document.write(htmlfile)
        print(f'{htmlfile} has been saved successfully!')
        if open:
          webbrowser.open_new_tab(htmlfile)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.save()
        except Exception as e:
            print(f'Can\'t save html. {e})')

    def __enter__(self):
        return self

    @staticmethod
    def __test__():
        with HTML_Report('test') as doc:
            doc.add_header("Test report")
            doc.add_text('this is text  ' * 20)
            doc.add_line_break()

            import numpy as np, datetime

            ts = pd.Series(np.random.randn(1000))
            ts = ts.cumsum()
            plot = ts.plot()
            fig = plot.get_figure()
            doc.add_fig(fig)
            

            arrays = [np.array(['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux']),
                    np.array(['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two'])]
            df = pd.DataFrame(np.random.randn(8, 4), index=arrays)
            doc.add_df(df)

            timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            doc.add_text(f'Created at {timestr}')
    
    def add_footer(self, text):
        self.footer +=text    

if __name__ == "__main__":
    HTML_Report.__test__()
