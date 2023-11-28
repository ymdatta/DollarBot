"""

MIT License

Copyright (c) 2021 Dev Kumar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from code import graphing
from mock import ANY

dummy_total_text_none = ""
dummy_total_text_data = """Food $10.0
Transport $50.0
Shopping $148.0
Miscellaneous $47.93
Utilities $200.0
Groceries $55.21\n"""
dummy_budget = "100.0"

dummy_x = ['Food', 'Transport', 'Shopping', 'Miscellaneous', 'Utilities', 'Groceries']
dummy_y = [10.0, 50.0, 148.0, 47.93, 200.0, 55.21]
dummy_categ_val = {'Food': 10.0, 'Transport': 50.0, 'Shopping': 148.0, 'Miscellaneous': 47.93, 'Miscellaneous': 47.93, 'Utilities': 200.0, 'Groceries': 55.21}
dummy_color = ['red', 'cornflowerblue', 'greenyellow', 'orange', 'violet', 'grey']
dummy_edgecolor = 'black'


def test_visualize(mocker):
    mocker.patch.object(graphing, 'plt')
    graphing.plt.bar.return_value = True
    graphing.visualize(dummy_total_text_data, dummy_budget)
    graphing.plt.bar.assert_called_with(dummy_categ_val.keys(), ANY, color=dummy_color, edgecolor=dummy_edgecolor)
