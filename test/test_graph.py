from code import graphing
from mock import ANY

dummy_total_text_none = ""
dummy_total_text_data = """Food $10.0
Transport $50.0
Shopping $148.0
Miscellaneous $47.93
Utilities $200.0
Groceries $55.21\n"""

dummy_x = ['Food', 'Transport', 'Shopping', 'Miscellaneous', 'Utilities', 'Groceries']
dummy_y = [10.0, 50.0, 148.0, 47.93, 200.0, 55.21]
dummy_categ_val = {'Food': 10.0, 'Transport': 50.0, 'Shopping': 148.0, 'Miscellaneous': 47.93, 'Miscellaneous': 47.93, 'Utilities': 200.0, 'Groceries': 55.21}
dummy_color = [(1.00, 0, 0, 0.6), (0.2, 0.4, 0.6, 0.6), (0, 1.00, 0, 0.6), (1.00, 1.00, 0, 1.00)]
dummy_edgecolor = 'blue'


def test_visualize(mocker):
    mocker.patch.object(graphing, 'plt')
    graphing.plt.bar.return_value = True
    graphing.visualize(dummy_total_text_data)
    graphing.plt.bar.assert_called_with(dummy_categ_val.keys(), ANY, color=dummy_color, edgecolor=dummy_edgecolor)
    
