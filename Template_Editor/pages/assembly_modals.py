import datetime

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback

from Template_Editor.controllers.template_handler_instance import template_handler_instance as template
# Workaround import since files in pages folder import classes as Template_Editor.mcnp_cards.<Class>
# do not compare correctly with mcnp_cards.<Class>
from Template_Editor.models.mcnp_cards import LikeCell


@callback(
    Output("plate_modal", "is_open"),
    Input("legacy_plate_open", "n_clicks"),
    Input("plate_close", "n_clicks"),
    State("plate_modal", "is_open"),
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    Output("legacy_plate_cell_selector", "options"),
    Output("legacy_plate_cell_selector", "value"),
    Input("legacy_plate_open", "n_clicks"),
    State("legacy_assembly_selector", "value"),
    State("legacy_plate_selector", "value"),
)
def modal_display(plate_button, assembly_u, plate_u):
    if assembly_u is not None and plate_u is not None:
        if plate_u == "All Plates":
            plate_options = ["All Sections"]
        else:
            plate_options = [o.number for o in template.all_fuel_plates.get(plate_u)]
        plate_options.sort()

        return plate_options, plate_options[0]
    return [], ""


@callback(
    Output("legacy_current_material", "value"),
    Input("legacy_plate_cell_selector", "value"),
    State("legacy_plate_selector", "value"),
)
def update_material(section_cell, plate_u):
    if plate_u is not None:
        if plate_u == "All Plates":
            return "Many"
        else:
            if section_cell is not None and template.all_fuel_plates.get(plate_u) is not None:
                for section in template.all_fuel_plates.get(plate_u):
                    if section.number == section_cell:
                        return section.material
    return ""


@callback(
    Output('console_output', 'children', allow_duplicate=True),
    Output('legacy_assembly_description', 'value', allow_duplicate=True),
    Input("legacy_plate_apply", "n_clicks"),
    State('legacy_assembly_selector', 'value'),
    State('legacy_assembly_description', 'children'),
    State("legacy_plate_selector", "value"),
    State("legacy_plate_cell_selector", "value"),
    State("legacy_current_material", "value"),
    State("legacy_new_material", "value"),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def plate_apply_changes(plate_apply_button, assembly_u, descr, plate_u, section_cell, curr_mat, new_mat,
                        current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'legacy_plate_apply' and None not in [plate_u, section_cell, curr_mat, new_mat]:
        if template.all_materials.get(new_mat) is None:
            message = f'({timestamp})\tError: Material not found'
            current_messages.insert(0, html.P(message))
            return current_messages, ""
        if plate_u == "All Plates":
            for plate in template.all_fuel_assemblies.get(assembly_u).plates:
                for sect in template.all_fuel_plates.get(plate):
                    sect.material = new_mat
                    if type(sect) is LikeCell:
                        template.dissect_like_param(sect)
            message = f'({timestamp})\tApplied changes made to all plate sections'
            current_messages.insert(0, html.P(message))
            return current_messages, ""
        else:
            if section_cell == "All Sections":
                pass
            else:
                selected_cell = None
                # Search for section
                for section in template.all_fuel_plates.get(plate_u):
                    if section.number == section_cell:
                        selected_cell = section

                if selected_cell is None:
                    message = f'({timestamp})\tError: Section not found'
                    current_messages.insert(0, html.P(message))
                    return current_messages, ""
                selected_cell.material = new_mat
                template.dissect_like_param(selected_cell)
                message = f'({timestamp})\tApplied changes made to Cell {selected_cell.number}'
                current_messages.insert(0, html.P(message))
                return current_messages, ""
    return current_messages, ""


plate_modal = dbc.Modal(id="plate_modal",
                        children=[dbc.ModalHeader("Edit Plate Attributes"),
                                  dbc.ModalBody(
                                      [
                                          dbc.Label("Section:"),
                                          dcc.Dropdown(id='legacy_plate_cell_selector',
                                                       placeholder='Select a Plate',
                                                       clearable=True,
                                                       persistence=True, persistence_type='session',
                                                       className='dropdown'),
                                          dbc.Row([
                                              dbc.Col([
                                                  dbc.Label("Current Material:"),
                                                  dbc.Input(id="legacy_current_material", type="text",
                                                            placeholder="Enter new value")
                                              ]),
                                              dbc.Col([
                                                  dbc.Label("New Material:"),
                                                  dbc.Input(id="legacy_new_material", type="text",
                                                            placeholder="Enter new value")
                                              ])
                                          ])
                                      ]
                                  ),
                                  dbc.ModalFooter([
                                      dbc.Button("Apply Changes", id="legacy_plate_apply", className="ml-auto"),
                                      dbc.Button("Close", id="plate_close", className="ml-auto")
                                  ]),
                                  ],
                        is_open=False, modal_class_name='assembly-modal')
