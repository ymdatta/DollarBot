import unittest
from unittest.mock import Mock, patch
from code import download_pdf  


@patch('code.download_pdf.plt.subplots')
def test_generate_expense_history_plot_no_records(mock_subplots):
    user_history = []
    fig, ax = Mock(), Mock()
    mock_subplots.return_value = (fig, ax)

    result = download_pdf.generate_expense_history_plot(user_history)

    assert result is not None
    ax.text.assert_called_once()


@patch('code.download_pdf.plt.subplots')
def test_generate_expense_history_plot_with_records(mock_subplots):
    user_history = ["2023-01-01,Food,50,Cash", "2023-01-02,Transport,20,Card"]
    fig, ax = Mock(), Mock()
    mock_subplots.return_value = (fig, ax)

    result = download_pdf.generate_expense_history_plot(user_history)

    assert result is not None
    ax.text.assert_called()


if __name__ == '__main__':
    unittest.main()
