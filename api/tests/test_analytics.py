# import pytest
# from fastapi.testclient import TestClient

# from api.app import app

# client = TestClient(app)


# # Test to ensure the analytics endpoint exists and returns a valid response
# def test_endpoint_exists():
#     response = client.get("/analytics")
#     assert response.status_code in [
#         200,
#         422,
#     ]  # Depending on whether x_var, y_var, and graph_type are provided


# # Test for default parameters, verifying it returns an HTML response with an image
# def test_default_parameters():
#     response = client.get("/analytics?x_var=date&y_var=amount&graph_type=line")
#     assert response.status_code == 200
#     assert '<img src="data:image/png;base64,' in response.text


# # Test for line graph with valid parameters
# def test_line_graph():
#     response = client.get("/analytics?x_var=date&y_var=amount&graph_type=line")
#     assert response.status_code == 200
#     assert '<img src="data:image/png;base64,' in response.text


# # Test for bar graph with valid parameters
# def test_bar_graph():
#     response = client.get("/analytics?x_var=category&y_var=amount&graph_type=bar")
#     assert response.status_code == 200
#     assert '<img src="data:image/png;base64,' in response.text


# # Test for pie chart with valid parameters
# def test_pie_chart():
#     response = client.get("/analytics?x_var=category&y_var=amount&graph_type=pie")
#     assert response.status_code == 200
#     assert '<img src="data:image/png;base64,' in response.text


# # Test for invalid graph type; should return a 422 error
# def test_invalid_graph_type():
#     response = client.get("/analytics?x_var=date&y_var=amount&graph_type=invalid")
#     assert response.status_code == 422
#     assert response.json() == {"detail": "Invalid graph type"}


# # Test for invalid x and y variables; should return a 422 error
# def test_invalid_x_y_variables():
#     response = client.get("/analytics?x_var=NonExistent&y_var=amount")
#     assert response.status_code == 422
#     assert response.json() == {"detail": "Invalid x or y variable"}


# # Test for missing parameters; should return a 422 error if any required parameters are missing
# def test_missing_parameters():
#     response = client.get("/analytics?x_var=date")
#     assert response.status_code == 422
#     assert response.json() == {"detail": "Invalid x or y variable"}
