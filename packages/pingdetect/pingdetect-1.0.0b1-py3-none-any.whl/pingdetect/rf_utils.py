
'''
Copyright (c) 2025 Cameron S. Bodine
'''

import os, sys
from inference.models.utils import get_roboflow_model
from inference import get_model
from distutils.dir_util import copy_tree
import shutil
from pingdetect.version import __version__
import json

USER_DIR = os.path.expanduser('~')

import PySimpleGUI as sg

def get_model(utils_dir: str,):

    '''
    Download a roboflow model and save to destination
    '''

    ############
    # Set Up GUI

    # Title #
    title = sg.Text("PINGDetect: Roboflow Utils", font=("Helvetica", 24), justification="center", size=(75, 1))
    version = sg.Text("ver. {}".format(__version__), font=("Helvetica", 8), justification="center", size=(75, 1))

    # Instructions #
    instructions = sg.Text("Enter your Roboflow API key below. You can get your API key from your Roboflow account page.", font=("Helvetica", 12), justification="left", size=(75, 2))
    
    # RF API Key #
    api_key_label = sg.Text("Roboflow API Key:", size=(20, 1), font=("Helvetica", 12), justification="left")
    api_key_input = sg.InputText(size=(40, 1), font=("Helvetica", 12), key='API_KEY')

    # RF Project Name #
    proj_name_label = sg.Text("Project Name:", size=(20, 1), font=("Helvetica", 12), justification="left")
    proj_name_input = sg.InputText(size=(40, 1), font=("Helvetica", 12), key='PROJ_NAME')

    # RF Project Version #
    proj_ver_label = sg.Text("Project Version:", size=(20, 1), font=("Helvetica", 12), justification="left")
    proj_ver_input = sg.InputText(size=(40, 1), font=("Helvetica", 12), key='PROJ_VER')

    # Buttons #
    submit_button = sg.Button("Submit", font=("Helvetica", 12), size=(10, 1), bind_return_key=True)
    cancel_button = sg.Button("Cancel", font=("Helvetica", 12), size=(10, 1))

    #############
    # Exit Button
    exit_btn = sg.Button("Quit", key="exit_pingdetect", font=("Helvetica", 12, "bold"), button_color="darkred", size=(10, 1))

    layout = [
        [title],
        [version],
        [instructions],
        [api_key_label, api_key_input],
        [proj_name_label, proj_name_input],
        [proj_ver_label, proj_ver_input],
        [submit_button, cancel_button],
        [sg.HorizontalSeparator()],
        [sg.HorizontalSeparator()],
        [exit_btn],
    ]

    layout2 =[[sg.Column(layout, scrollable=True,  vertical_scroll_only=True, size_subsample_height=1)]]
    window = sg.Window('PINGDetect', layout2, resizable=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'exit_pingdetect' or event == 'Cancel':
            print('Exiting.')
            sys.exit()
        if event == 'Submit':
            my_api_key, my_model_name, my_model_ver = saveModelParams(values, utils_dir)
            break

    window.close()
    #########
    # End GUI

    # rf = roboflow.Roboflow(api_key=my_api_key)
    # workspace = rf.workspace()
    # print(workspace)
    # print(rf.workspace().project(my_model_name).versions())
    # sys.exit()

    # Read model params
    my_model_id = '{}/{}'.format(my_model_name, my_model_ver)

    # Get the model
    model = get_roboflow_model(model_id=my_model_id, api_key=my_api_key)

    # Copy the model
    source_dir = os.path.join("/tmp/cache", my_model_id)
    dest_dir = os.path.join(utils_dir, 'models', my_model_id)

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)

    # Delete the source dir
    source_dir = os.path.dirname(source_dir)
    shutil.rmtree(source_dir)

    return


def saveModelParams(values: dict, out_dir: str):
    '''
    Save the model parameters to a json file.
    '''

    my_api_key = values['API_KEY']
    my_model_name = values['PROJ_NAME']
    my_model_version = values['PROJ_VER']

    out_file = os.path.join(out_dir, 'rf_{}_{}_params.json'.format(my_model_name, my_model_version))

    # Delete file if exists
    if os.path.exists(out_file):
        os.remove(out_file)

    if len(my_api_key) < 20 or len(my_model_name) < 3 or len(my_model_version) < 1:
        print('Invalid input. Exiting.')
        sys.exit()

    with open(out_file, 'w') as f:
        f.write('{"rf_api_key": "' + my_api_key + '", "my_model_name": "' + my_model_name + '", "my_model_version": "' + my_model_version + '"}')

    return my_api_key, my_model_name, my_model_version

    