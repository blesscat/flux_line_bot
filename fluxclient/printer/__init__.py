def binary(key, value):
    if value == '0' or value == '1':
        return 'ok'
    else:
        return "Invalid value: '%s' for '%s', must be 1 or 0" % (value, key)


def constant(key, value):
    return "You can\'t change this setting: '%s'" % key


def free(key, value):
    return 'ok'


def ignore(key, value):
    return 'ignore'


def percentage(key, value, start=0, end=100):
    tmp_value = value.rstrip('%')
    return int_range(key, tmp_value, start, end)


def float_range(key, value, start=float('-inf'), end=float('inf')):
    try:
        tmp_value = float(value)
    except:
        return "Invalid value: '%s', must be a float" % value
    else:
        if start <= tmp_value and tmp_value <= end:
            return 'ok'
        else:
            return "Invalid value: %s for '%s', must be within [%f-%f]" % (value, key, start, end)


def int_range(key, value, start=float('-inf'), end=float('inf')):
    try:
        tmp_value = int(value)
    except:
        return "Invalid value: '%s' for '%s', must be a integer" % (value, key)
    else:
        if start <= tmp_value and tmp_value <= end:
            return 'ok'
        else:
            return "Invalid value: '%s' for '%s', must be within [%d-%d]" % (value, key, start, end)


def finite_choice(key, value, white_list):
    if value in white_list:
        return 'ok'
    else:
        return "Invalid value: '%s' for '%s', must be one of %s" % (value, key, repr(white_list)[1:-1])


def hex_color(key, value):
    value = value.upper()
    try:
        assert value[1] != '#'
        value = value.lstrip('#')
        assert len(value) == 6
        if all(j <= 255 for j in [int(value[i:i + len(value) // 3], 16) for i in range(0, len(value), len(value) // 3)]):
            return 'ok'
        else:
            raise
    except:
        return "Invalid value: '%s' for %s, must be a hex color" % (value, key)


def float_or_percent(key, value, percent_start=float('-inf'), percent_end=float('inf'), float_start=float('-inf'), float_end=float('inf')):
    m = "Invalid value: '%s' for '%s', must be float or percentage" % (value, key)

    try:
        if value.endswith('%'):
            v = float(value[:-1])
            if v >= percent_start and v <= percent_end:
                m = 'ok'
        else:
            if float(value) >= float_start and float(value) <= float_end:
                m = 'ok'
    except:
        pass
    finally:
        return m


ini_string = """# generated by Slic3r 1.2.9 on Tue Nov 10 23:28:47 2015
avoid_crossing_perimeters = 0
bed_shape = 84.5344x8.88492,83.1425x17.6725,80.8398x26.2664,77.6514x34.5726,73.6122x42.5,68.7664x49.9617,63.1673x56.8761,56.8761x63.1673,49.9617x68.7664,42.5x73.6122,34.5726x77.6514,26.2664x80.8398,17.6725x83.1425,8.88492x84.5344,0x85,-8.88492x84.5344,-17.6725x83.1425,-26.2664x80.8398,-34.5726x77.6514,-42.5x73.6122,-49.9617x68.7664,-56.8761x63.1673,-63.1673x56.8761,-68.7664x49.9617,-73.6122x42.5,-77.6514x34.5726,-80.8398x26.2664,-83.1425x17.6725,-84.5344x8.88492,-85x0,-84.5344x-8.88492,-83.1425x-17.6725,-80.8398x-26.2664,-77.6514x-34.5726,-73.6122x-42.5,-68.7664x-49.9617,-63.1673x-56.8761,-56.8761x-63.1673,-49.9617x-68.7664,-42.5x-73.6122,-34.5726x-77.6514,-26.2664x-80.8398,-17.6725x-83.1425,-8.88492x-84.5344,0x-85,8.88492x-84.5344,17.6725x-83.1425,26.2664x-80.8398,34.5726x-77.6514,42.5x-73.6122,49.9617x-68.7664,56.8761x-63.1673,63.1673x-56.8761,68.7664x-49.9617,73.6122x-42.5,77.6514x-34.5726,80.8398x-26.2664,83.1425x-17.6725,84.5344x-8.88492,85x0
bed_temperature = 0
before_layer_gcode =
bottom_solid_layers = 3
bridge_acceleration = 0
bridge_fan_speed = 100
bridge_flow_ratio = 1
bridge_speed = 20
brim_width = 0
complete_objects = 0
cooling = 1
default_acceleration = 0
disable_fan_first_layers = 5
dont_support_bridges = 1
duplicate_distance = 6
end_gcode = M104 S0 ; turn off temperature\\nG91\\nG1 E-1 F300\\nG1 Z+5 E-5 F9000\\nG28 X0  ; home X axis\\nM84     ; disable motors\\n
external_fill_pattern = rectilinear
external_perimeter_extrusion_width = 0.4
external_perimeter_speed = 70%
external_perimeters_first = 0
extra_perimeters = 1
extruder_clearance_height = 20
extruder_clearance_radius = 20
extruder_offset = 0x0
extrusion_axis = E
extrusion_multiplier = 1
extrusion_width = 0.4
fan_always_on = 0
fan_below_layer_time = 15
filament_colour = #FFFFFF
filament_diameter = 1.75
fill_angle = 45
fill_density = 20%
fill_pattern = honeycomb
first_layer_acceleration = 0
first_layer_bed_temperature = 0
first_layer_extrusion_width = 120%
first_layer_height = 0.35
first_layer_speed = 20
first_layer_temperature = 220
gap_fill_speed = 20
gcode_arcs = 0
gcode_comments = 0
gcode_flavor = reprap
infill_acceleration = 0
infill_every_layers = 1
infill_extruder = 1
infill_extrusion_width = 0.4
infill_first = 0
infill_only_where_needed = 0
infill_overlap = 15%
infill_speed = 50
interface_shells = 0
layer_gcode =
layer_height = 0.2
max_fan_speed = 100
max_print_speed = 50
max_volumetric_speed = 0
min_fan_speed = 80
min_print_speed = 3
min_skirt_length = 0
notes =
nozzle_diameter = 0.4
octoprint_apikey =
octoprint_host =
only_retract_when_crossing_perimeters = 1
ooze_prevention = 0
output_filename_format = [input_filename_base].gcode
overhangs = 0
perimeter_acceleration = 0
perimeter_extruder = 1
perimeter_extrusion_width = 0.4
perimeter_speed = 30
perimeters = 3
post_process =
pressure_advance = 0
raft_layers = 0
resolution = 0.01
retract_before_travel = 2
retract_layer_change = 0
retract_length = 5.5
retract_length_toolchange = 10
retract_lift = 0.1
retract_restart_extra = 0
retract_restart_extra_toolchange = 0
retract_speed = 60
seam_position = aligned
skirt_distance = 20
skirt_height = 1
skirts = 1
slowdown_below_layer_time = 15
small_perimeter_speed = 15
solid_infill_below_area = 70
solid_infill_every_layers = 0
solid_infill_extruder = 1
solid_infill_extrusion_width = 0.4
solid_infill_speed = 20
spiral_vase = 0
standby_temperature_delta = -5
start_gcode = G1 Z5 F5000 ; lift nozzle\\n
support_material = 1
support_material_angle = 0
support_material_contact_distance = 0.2
support_material_enforce_layers = 0
support_material_extruder = 1
support_material_extrusion_width = 0.4
support_material_interface_extruder = 1
support_material_interface_layers = 3
support_material_interface_spacing = 0
support_material_interface_speed = 100%
support_material_pattern = rectilinear-grid
support_material_spacing = 2
support_material_speed = 40
support_material_threshold = 55
temperature = 210
thin_walls = 0
threads = 2
toolchange_gcode =
top_infill_extrusion_width = 0.4
top_solid_infill_speed = 15
top_solid_layers = 4
travel_speed = 80
use_firmware_retraction = 0
use_relative_e_distances = 0
use_volumetric_e = 0
vibration_limit = 0
wipe = 0
xy_size_compensation = 0
z_offset = -1
flux_refill_empty = 0
flux_first_layer = 0
flux_raft = 0
cut_bottom = -1
detect_filament_runout = 1
detect_head_shake = 1
detect_head_tilt = 1
flux_calibration = 1
pause_at_layers = 
support_everywhere = 0"""

ini_constraint = {
    'avoid_crossing_perimeters': [binary],
    'bed_shape': [ignore],
    'bed_temperature': [ignore],
    'before_layer_gcode': [free],
    'bottom_solid_layers': [int_range, 0, 20],
    'bridge_acceleration': [binary],
    'bridge_fan_speed': [percentage],
    'bridge_flow_ratio': False,
    'bridge_speed': [int_range, 1, 150],
    'brim_width': [int_range, 0, 99],
    'complete_objects': False,
    'cooling': [binary],
    'default_acceleration': False,
    'disable_fan_first_layers': [int_range, 0],
    'dont_support_bridges': [binary],
    'duplicate_distance': False,
    'end_gcode': [free],
    'external_fill_pattern': [finite_choice, ['rectilinear-grid', 'line', 'rectilinear', 'honeycomb', 'AUTOMATIC', 'GRID', 'LINES', 'CONCENTRIC']],
    'external_perimeter_extrusion_width': False,
    'external_perimeter_speed': [float_or_percent],
    'external_perimeters_first': False,
    'extra_perimeters': [binary],
    'extruder_clearance_height': False,
    'extruder_clearance_radius': False,
    'extruder_offset': [ignore],
    'extrusion_axis': False,
    'extrusion_multiplier': False,
    'extrusion_width': False,
    'fan_always_on': [binary],
    'fan_below_layer_time': [int_range, 0],
    'filament_colour': [ignore],
    'filament_diameter': False,
    'fill_angle': False,
    'fill_density': [percentage],
    'fill_pattern': [finite_choice, ['rectilinear-grid', 'line', 'rectilinear', 'honeycomb', 'AUTOMATIC', 'GRID', 'LINES', 'CONCENTRIC']],
    'first_layer_acceleration': [binary],
    'first_layer_bed_temperature': [ignore],
    'first_layer_extrusion_width': [percentage, 0, 1666],
    'first_layer_height': [float_range, 0.02, 0.4],
    'first_layer_speed': [int_range, 1, 150],
    'first_layer_temperature': [int_range, 10, 230],
    'gap_fill_speed': [int_range, 1, 150],
    'gcode_arcs': False,
    'gcode_comments': [ignore],
    'gcode_flavor': [free],
    'infill_acceleration': [binary],
    'infill_every_layers': [int_range, 0],
    'infill_extruder': False,
    'infill_extrusion_width': False,
    'infill_first': False,
    'infill_only_where_needed': False,
    'infill_overlap': [percentage],
    'infill_speed': [int_range, 1, 150],
    'interface_shells': False,
    'layer_gcode': False,
    'layer_height': [float_range, 0.02, 0.4],
    'max_fan_speed': [percentage],
    'max_print_speed': False,
    'max_volumetric_speed': False,
    'min_fan_speed': [int_range, 0, 100],
    'min_print_speed': False,
    'min_skirt_length': False,
    'notes': False,
    'nozzle_diameter': [float_range],
    'octoprint_apikey': [ignore],
    'octoprint_host': [ignore],
    'only_retract_when_crossing_perimeters': [binary],
    'ooze_prevention': [binary],
    'output_filename_format': [free],
    'overhangs': [binary],
    'perimeter_acceleration': False,
    'perimeter_extruder': False,
    'perimeter_extrusion_width': False,
    'perimeter_speed': [int_range, 1, 150],
    'perimeters': [int_range, 0, 20],
    'post_process': False,
    'pressure_advance': False,
    'raft_layers': [int_range, 0, 20],
    'resolution': False,
    'retract_before_travel': False,
    'retract_layer_change': False,
    'retract_length': False,
    'retract_length_toolchange': False,
    'retract_lift': False,
    'retract_restart_extra': False,
    'retract_restart_extra_toolchange': False,
    'retract_speed': False,
    'seam_position': False,
    'skirt_distance': [float_range, 0],
    'skirt_height': [int_range, 0],
    'skirts': [int_range, 0, 20],
    'slowdown_below_layer_time': [int_range, 0],
    'small_perimeter_speed': False,
    'solid_infill_below_area': False,
    'solid_infill_every_layers': [int_range, 0],
    'solid_infill_extruder': False,
    'solid_infill_extrusion_width': False,
    'solid_infill_speed': [int_range, 1, 150],
    'spiral_vase': [binary],
    'standby_temperature_delta': [int_range, -400, 400],
    'start_gcode': False,
    'support_everywhere': [binary],
    'support_material': [binary],
    'support_material_angle': False,
    'support_material_contact_distance': [float_range, 0.0, 10],
    'support_material_enforce_layers': False,
    'support_material_extruder': False,
    'support_material_extrusion_width': False,
    'support_material_interface_extruder': False,
    'support_material_interface_layers': False,
    'support_material_interface_spacing': False,
    'support_material_interface_speed': [percentage],
    'support_material_pattern': [finite_choice, ['rectilinear-grid', 'line', 'rectilinear', 'honeycomb', 'GRID', 'LINES']],
    'support_material_spacing': False,
    'support_material_speed': [int_range, 1, 150],
    'support_material_threshold': [int_range, 0, 90],
    'temperature': [int_range, 10, 230],
    'thin_walls': [binary],
    'threads': False,
    'toolchange_gcode': False,
    'top_infill_extrusion_width': False,
    'top_solid_infill_speed': [int_range, 1, 150],
    'top_solid_layers': [int_range, 0, 20],
    'travel_speed': [int_range, 1, 150],
    'use_firmware_retraction': [binary],
    'use_relative_e_distances': [binary],
    'use_volumetric_e': [binary],
    'vibration_limit': [free],
    'wipe': False,
    'xy_size_compensation': False,
    'z_offset': [float_range, -10, 10],
    'flux_refill_empty': [binary],
    'flux_first_layer': [binary],
    'flux_raft': [binary],
    'cut_bottom': [float_range, -1, 240],
    'detect_filament_runout': [binary],
    'detect_head_shake': [binary],
    'detect_head_tilt': [binary],
    'flux_calibration': [binary],
    'pause_at_layers': False
}

ini_flux_params = ['cut_bottom' ,'flux_', 'detect_', 'pause_at_layers']
