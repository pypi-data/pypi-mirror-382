import webbrowser


# def do_track():
#     consignmentnum = 39
#     postcode = 'TF1 2NP'
#     url = r'https://apcchoice.apc-overnight.com/APCChoice'
#


import requests
import webbrowser
import tempfile


def do_track(consignment_number: int, postcode: str):
    url = 'https://apcchoice.apc-overnight.com/APCChoice'
    form_data = {'ConsignmentNumber': consignment_number, 'Postcode': postcode}

    response = requests.post(url, data=form_data)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name

    webbrowser.open(f'file://{temp_file_path}')


if __name__ == '__main__':
    do_track(39, 'TF1 2NP')
