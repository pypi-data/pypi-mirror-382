"""
General functions for OMGUI API endpoints.
"""


def landing():
    return "This is the OMGUI API"


def health():
    return ":)"


# Maybe later
# def exec_command(command=None):
#     """
#     Proof-of-concept to execute OpenAD commands.
#     """
#     import pandas
#     import IPython
#     from openad.app.main import api_remote
#     from IPython.core.formatters import format_display_data

#     response = api_remote(command)

#     # print("Parsing command:\n", command)
#     # print("Response:\n", response)

#     if hasattr(pandas.io.formats, "style") and isinstance(
#         response, pandas.io.formats.style.Styler
#     ):
#         # print("Response is pandas Styler object")
#         response = response.data

#     if isinstance(response, IPython.core.display.Markdown):
#         # print("Response is IPython Markdown object")

#         formatted, metadata = format_display_data(response)
#         response = formatted["text/markdown"]

#     if isinstance(response, pandas.core.frame.DataFrame):
#         # print("Response is pandas DataFrame")
#         response = response.to_csv()

#     if response:
#         return response, 200
#     else:
#         return "No result", 50
