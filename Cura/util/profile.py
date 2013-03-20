from __future__ import absolute_import
from __future__ import division

import os, traceback, math, re, zlib, base64, time, sys, platform, glob, string, stat, types
import cPickle as pickle
if sys.version_info[0] < 3:
	import ConfigParser
else:
	import configparser as ConfigParser

from Cura.util import resources
from Cura.util import version
from Cura.util import validators

settingsDictionary = {}
settingsList = []
class setting(object):
	def __init__(self, name, default, type, category, subcategory):
		self._name = name
		self._label = name
		self._tooltip = ''
		self._default = unicode(default)
		self._value = self._default
		self._type = type
		self._category = category
		self._subcategory = subcategory
		self._validators = []
		self._conditions = []

		if type is types.FloatType:
			validators.validFloat(self)
		elif type is types.IntType:
			validators.validInt(self)

		global settingsDictionary
		settingsDictionary[name] = self
		global settingsList
		settingsList.append(self)

	def setLabel(self, label, tooltip = ''):
		self._label = label
		self._tooltip = tooltip
		return self

	def setRange(self, minValue = None, maxValue = None):
		if len(self._validators) < 1:
			return
		self._validators[0].minValue = minValue
		self._validators[0].maxValue = maxValue
		return self

	def getLabel(self):
		return self._label

	def getTooltip(self):
		return self._tooltip

	def getCategory(self):
		return self._category

	def getSubCategory(self):
		return self._subcategory

	def isPreference(self):
		return self._category == 'preference'

	def isAlteration(self):
		return self._category == 'alteration'

	def isProfile(self):
		return not self.isAlteration() and not self.isPreference()

	def getName(self):
		return self._name

	def getType(self):
		return self._type

	def getValue(self):
		return self._value

	def getDefault(self):
		return self._default

	def setValue(self, value):
		self._value = unicode(value)

	def validate(self):
		result = validators.SUCCESS
		msgs = []
		for validator in self._validators:
			res, err = validator.validate()
			if res == validators.ERROR:
				result = res
			elif res == validators.WARNING and result != validators.ERROR:
				result = res
			if res != validators.SUCCESS:
				msgs.append(err)
		return result, '\n'.join(msgs)

	def addCondition(self, conditionFunction):
		self._conditions.append(conditionFunction)

	def checkConditions(self):
		for condition in self._conditions:
			if not condition():
				return False
		return True

#########################################################
## Settings
#########################################################
setting('layer_height',              0.2, float, 'basic',    'Quality').setRange(0.0001).setLabel('Layer height (mm)', 'Layer height in millimeters.\n0.2 is a good value for quick prints.\n0.1 gives high quality prints.\nDepending on your printer you can go as low as 0.02mm')
setting('wall_thickness',            0.8, float, 'basic',    'Quality').setRange(0.0001).setLabel('Wall thickness (mm)', 'Thickness of the walls.\nThis is used in combination with the nozzle size to define the number\nof perimeter lines and the thickness of those perimeter lines.')
setting('retraction_enable',       False, bool,  'basic',    'Quality').setLabel('Enable retraction', 'Retract the filament when the nozzle is moving over a none-printed area. Details about the retraction can be configured in the advanced tab.')
setting('solid_layer_thickness',     0.6, float, 'basic',    'Fill').setRange(0).setLabel('Bottom/Top thickness (mm)', 'This controls the thickness of the bottom and top layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiply of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.')
setting('fill_density',               20, float, 'basic',    'Fill').setRange(0, 100).setLabel('Fill Density (%)', 'This controls how densely filled the insides of your print will be. For a solid part use 100%, for an empty part use 0%. A value around 20% is usually enough.\nThis won\'t effect the outside of the print and only adjusts how strong the part becomes.')
setting('nozzle_size',               0.4, float, 'advanced', 'Machine').setRange(0.1,10).setLabel('Nozzle size (mm)', 'The nozzle size is very important, this is used to calculate the line width of the infill, and used to calculate the amount of outside wall lines and thickness for the wall thickness you entered in the print settings.')
setting('skirt_line_count',            1, int,   'advanced', 'Skirt').setRange(0).setLabel('Line count', 'The skirt is a line drawn around the object at the first layer. This helps to prime your extruder, and to see if the object fits on your platform.\nSetting this to 0 will disable the skirt. Multiple skirt lines can help priming your extruder better for small objects.')
setting('skirt_gap',                 3.0, float, 'advanced', 'Skirt').setRange(0).setLabel('Start distance (mm)', 'The distance between the skirt and the first layer.\nThis is the minimal distance, multiple skirt lines will be put outwards from this distance.')
setting('print_speed',                50, float, 'basic',    'Speed & Temperature').setRange(1).setLabel('Print speed (mm/s)', 'Speed at which printing happens. A well adjusted Ultimaker can reach 150mm/s, but for good quality prints you want to print slower. Printing speed depends on a lot of factors. So you will be experimenting with optimal settings for this.')
setting('print_temperature',         220, int,   'basic',    'Speed & Temperature').setRange(0,340).setLabel('Printing temperature (C)', 'Temperature used for printing. Set at 0 to pre-heat yourself.\nFor PLA a value of 210C is usually used.\nFor ABS a value of 230C or higher is required.')
setting('print_temperature2',          0, int,   'basic',    'Speed & Temperature').setRange(0,340).setLabel('2nd nozzle temperature (C)', 'Temperature used for printing. Set at 0 to pre-heat yourself.\nFor PLA a value of 210C is usually used.\nFor ABS a value of 230C or higher is required.')
setting('print_temperature3',          0, int,   'basic',    'Speed & Temperature').setRange(0,340).setLabel('3th nozzle temperature (C)', 'Temperature used for printing. Set at 0 to pre-heat yourself.\nFor PLA a value of 210C is usually used.\nFor ABS a value of 230C or higher is required.')
setting('print_temperature4',          0, int,   'basic',    'Speed & Temperature').setRange(0,340).setLabel('4th nozzle temperature (C)', 'Temperature used for printing. Set at 0 to pre-heat yourself.\nFor PLA a value of 210C is usually used.\nFor ABS a value of 230C or higher is required.')
setting('print_bed_temperature',      70, int,   'basic',    'Speed & Temperature').setRange(0,340).setLabel('Bed temperature (C)', 'Temperature used for the heated printer bed. Set at 0 to pre-heat yourself.')
setting('support',                'None', ['None', 'Touching buildplate', 'Everywhere'], 'Basic', 'Support structure').setLabel('Support type', 'Type of support structure build.\n"Exterior only" is the most commonly used support setting.\n\nNone does not do any support.\nTouching buildplate only creates support where the support structure will touch the build platform.\nEverywhere creates support even on top of parts of the model.')
setting('enable_raft',             False, bool,  'basic',   'Support').setLabel('Enable raft', 'A raft is a few layers of lines below the bottom of the object. It prevents warping. Full raft settings can be found in the expert settings.\nFor PLA this is usually not required. But if you print with ABS it is almost required.')
setting('support_dual_extrusion',  False, bool, 'basic', 'Support').setLabel('Support dual extrusion', 'Print the support material with the 2nd extruder in a dual extrusion setup. The primary extruder will be used for normal material, while the second extruder is used to print support material.')
setting('filament_diameter',        2.89, float, 'basic',    'Filament').setRange(1).setLabel('Diameter (mm)', 'Diameter of your filament, as accurately as possible.\nIf you cannot measure this value you will have to calibrate it, a higher number means less extrusion, a smaller number generates more extrusion.')
setting('filament_diameter2',          0, float, 'basic',    'Filament').setRange(0).setLabel('Diameter2 (mm)', 'Diameter of your filament for the 2nd nozzle. Use 0 to use the same diameter as for nozzle 1.')
setting('filament_diameter3',          0, float, 'basic',    'Filament').setRange(0).setLabel('Diameter3 (mm)', 'Diameter of your filament for the 3th nozzle. Use 0 to use the same diameter as for nozzle 1.')
setting('filament_diameter4',          0, float, 'basic',    'Filament').setRange(0).setLabel('Diameter4 (mm)', 'Diameter of your filament for the 4th nozzle. Use 0 to use the same diameter as for nozzle 1.')
setting('filament_density',         1.00, float, 'basic',    'Filament').setRange(0.5,1.5).setLabel('Packing Density', 'Packing density of your filament. This should be 1.00 for PLA and 0.85 for ABS')
setting('retraction_min_travel',     5.0, float, 'advanced', 'Retraction').setRange(0).setLabel('Minimum travel (mm)', 'Minimum amount of travel needed for a retraction to happen at all. To make sure you do not get a lot of retractions in a small area')
setting('retraction_speed',         40.0, float, 'advanced', 'Retraction').setRange(0.1).setLabel('Speed (mm/s)', 'Speed at which the filament is retracted, a higher retraction speed works better. But a very high retraction speed can lead to filament grinding.')
setting('retraction_amount',         4.5, float, 'advanced', 'Retraction').setRange(0).setLabel('Distance (mm)', 'Amount of retraction, set at 0 for no retraction at all. A value of 2.0mm seems to generate good results.')
setting('retraction_extra',          0.0, float, 'advanced', 'Retraction').setRange(0).setLabel('Extra length on start (mm)', 'Extra extrusion amount when restarting after a retraction, to better "Prime" your extruder after retraction.')
setting('bottom_thickness',          0.3, float, 'advanced', 'Quality').setRange(0).setLabel('Initial layer thickness (mm)', 'Layer thickness of the bottom layer. A thicker bottom layer makes sticking to the bed easier. Set to 0.0 to have the bottom layer thickness the same as the other layers.')
setting('object_sink',               0.0, float, 'advanced', 'Quality').setLabel('Cut off object bottom (mm)', 'Sinks the object into the platform, this can be used for objects that do not have a flat bottom and thus create a too small first layer.')
setting('enable_skin',             False, bool,  'advanced', 'Quality').setLabel('Duplicate outlines', 'Skin prints the outer lines of the prints twice, each time with half the thickness. This gives the illusion of a higher print quality.')
setting('travel_speed',            150.0, float, 'advanced', 'Speed').setRange(0.1).setLabel('Travel speed (mm/s)', 'Speed at which travel moves are done, a high quality build Ultimaker can reach speeds of 250mm/s. But some machines might miss steps then.')
setting('bottom_layer_speed',         20, float, 'advanced', 'Speed').setRange(0.1).setLabel('Bottom layer speed (mm/s)', 'Print speed for the bottom layer, you want to print the first layer slower so it sticks better to the printer bed.')
#setting('cool_min_layer_time',         5, float, 'advanced', 'Cool').setRange(0).setLabel('Minimal layer time (sec)', 'Minimum time spend in a layer, gives the layer time to cool down before the next layer is put on top. If the layer will be placed down too fast the printer will slow down to make sure it has spend at least this amount of seconds printing this layer.')
#setting('fan_enabled',              True, bool,  'advanced', 'Cool').setLabel('Enable cooling fan', 'Enable the cooling fan during the print. The extra cooling from the cooling fan is essensial during faster prints.')
#setting('max_z_speed',               3.0, float, 'expert',   'Speed').setRange(0.1).setLabel('Max Z speed (mm/s)', 'Speed at which Z moves are done. When you Z axis is properly lubricated you can increase this for less Z blob.')
#setting('retract_on_jumps_only',    True, bool,  'expert',   'Retraction').setLabel('Retract on jumps only', 'Only retract when we are making a move that is over a hole in the model, else retract on every move. This effects print quality in different ways.')
setting('fan_layer',                   1, int,   'expert',   'Cool').setRange(0).setLabel('Fan on layer number', 'The layer at which the fan is turned on. The first layer is layer 0. The first layer can stick better if you turn on the fan on, on the 2nd layer.')
#setting('fan_speed',                 100, int,   'expert',   'Cool').setRange(0,100).setLabel('Fan speed min (%)', 'When the fan is turned on, it is enabled at this speed setting. If cool slows down the layer, the fan is adjusted between the min and max speed. Minimal fan speed is used if the layer is not slowed down due to cooling.')
#setting('fan_speed_max',             100, int,   'expert',   'Cool').setRange(0,100).setLabel('Fan speed max (%)', 'When the fan is turned on, it is enabled at this speed setting. If cool slows down the layer, the fan is adjusted between the min and max speed. Maximal fan speed is used if the layer is slowed down due to cooling by more then 200%.')
#setting('cool_min_feedrate',          10, float, 'expert',   'Cool').setRange(0).setLabel('Minimum feedrate (mm/s)', 'The minimal layer time can cause the print to slow down so much it starts to ooze. The minimal feedrate protects against this. Even if a print gets slown down it will never be slower then this minimal feedrate.')
#setting('extra_base_wall_thickness', 0.0, float, 'expert',   'Accuracy').setRange(0).setLabel('Extra Wall thickness for bottom/top (mm)', 'Additional wall thickness of the bottom and top layers.')
#setting('sequence', 'Loops > Perimeter > Infill', ['Loops > Perimeter > Infill', 'Loops > Infill > Perimeter', 'Infill > Loops > Perimeter', 'Infill > Perimeter > Loops', 'Perimeter > Infill > Loops', 'Perimeter > Loops > Infill'], 'expert', 'Sequence')
#setting('force_first_layer_sequence', True, bool, 'expert', 'Sequence').setLabel('Force first layer sequence', 'This setting forces the order of the first layer to be \'Perimeter > Loops > Infill\'')
#setting('infill_type', 'Line', ['Line', 'Grid Circular', 'Grid Hexagonal', 'Grid Rectangular'], 'expert', 'Infill').setLabel('Infill pattern', 'Pattern of the none-solid infill. Line is default, but grids can provide a strong print.')
#setting('solid_top', True, bool, 'expert', 'Infill').setLabel('Solid infill top', 'Create a solid top surface, if set to false the top is filled with the fill percentage. Useful for cups/vases.')
#setting('fill_overlap', 15, int, 'expert', 'Infill').setRange(0,100).setLabel('Infill overlap (%)', 'Amount of overlap between the infill and the walls. There is a slight overlap with the walls and the infill so the walls connect firmly to the infill.')
#setting('support_rate', 50, int, 'expert', 'Support').setRange(0,100).setLabel('Material amount (%)', 'Amount of material used for support, less material gives a weaker support structure which is easier to remove.')
#setting('support_distance',  0.5, float, 'expert', 'Support').setRange(0).setLabel('Distance from object (mm)', 'Distance between the support structure and the object. Empty gap in which no support structure is printed.')
#setting('joris', False, bool, 'expert', 'Joris').setLabel('Spiralize the outer contour', '[Joris] is a code name for smoothing out the Z move of the outer edge. This will create a steady Z increase over the whole print. It is intended to be used with a single walled wall thickness to make cups/vases.')
#setting('bridge_speed', 100, int, 'expert', 'Bridge').setRange(0,100).setLabel('Bridge speed (%)', 'Speed at which layers with bridges are printed, compared to normal printing speed.')
#setting('raft_margin', 5, float, 'expert', 'Raft').setRange(0).setLabel('Extra margin (mm)', 'If the raft is enabled, this is the extra raft area around the object which is also rafted. Increasing this margin will create a stronger raft.')
#setting('raft_base_material_amount', 100, int, 'expert', 'Raft').setRange(0,100).setLabel('Base material amount (%)', 'The base layer is the first layer put down as a raft. This layer has thick strong lines and is put firmly on the bed to prevent warping. This setting adjust the amount of material used for the base layer.')
#setting('raft_interface_material_amount', 100, int, 'expert', 'Raft').setRange(0,100).setLabel('Interface material amount (%)', 'The interface layer is a weak thin layer between the base layer and the printed object. It is designed to has little material to make it easy to break the base off the printed object. This setting adjusts the amount of material used for the interface layer.')
#setting('hop_on_move', False, bool, 'expert', 'Hop').setLabel('Enable hop on move', 'When moving from print position to print position, raise the printer head 0.2mm so it does not knock off the print (experimental).')

setting('model_matrix', '1,0,0,0,1,0,0,0,1', str, 'hidden', 'hidden')
setting('plugin_config', '', str, 'hidden', 'hidden')
setting('object_center_x', -1, float, 'hidden', 'hidden')
setting('object_center_y', -1, float, 'hidden', 'hidden')

setting('start.gcode', """;Sliced {filename} at: {day} {date} {time}
;Basic settings: Layer height: {layer_height} Walls: {wall_thickness} Fill: {fill_density}
;Print time: {print_time}
;Filament used: {filament_amount}m {filament_weight}g
;Filament cost: {filament_cost}
G21        ;metric values
G90        ;absolute positioning
M107       ;start with the fan off

G28 X0 Y0  ;move X/Y to min endstops
G28 Z0     ;move Z to min endstops

G1 Z15.0 F{max_z_speed} ;move the platform down 15mm

G92 E0                  ;zero the extruded length
G1 F200 E3              ;extrude 3mm of feed stock
G92 E0                  ;zero the extruded length again
G1 F{travel_speed}
M117 Printing...
""", str, 'alteration', 'alteration')
#######################################################################################
setting('end.gcode', """;End GCode
M104 S0                     ;extruder heater off
M140 S0                     ;heated bed heater off (if you have it)

G91                                    ;relative positioning
G1 E-1 F300                            ;retract the filament a bit before lifting the nozzle, to release some of the pressure
G1 Z+0.5 E-5 X-20 Y-20 F{travel_speed} ;move Z up a bit and retract filament even more
G28 X0 Y0                              ;move X/Y to min endstops, so the head is out of the way

M84                         ;steppers off
G90                         ;absolute positioning
""", str, 'alteration', 'alteration')
#######################################################################################
setting('support_start.gcode', '', str, 'alteration', 'alteration')
setting('support_end.gcode', '', str, 'alteration', 'alteration')
setting('cool_start.gcode', '', str, 'alteration', 'alteration')
setting('cool_end.gcode', '', str, 'alteration', 'alteration')
setting('replace.csv', '', str, 'alteration', 'alteration')
#######################################################################################
setting('nextobject.gcode', """;Move to next object on the platform. clear_z is the minimal z height we need to make sure we do not hit any objects.
G92 E0

G91                                    ;relative positioning
G1 E-1 F300                            ;retract the filament a bit before lifting the nozzle, to release some of the pressure
G1 Z+0.5 E-5 F{travel_speed}           ;move Z up a bit and retract filament even more
G90                                    ;absolute positioning

G1 Z{clear_z} F{max_z_speed}
G92 E0
G1 X{object_center_x} Y{object_center_y} F{travel_speed}
G1 F200 E6
G92 E0
""", str, 'alteration', 'alteration')
#######################################################################################
setting('switchExtruder.gcode', """;Switch between the current extruder and the next extruder, when printing with multiple extruders.
G92 E0
G1 E-36 F5000
G92 E0
T{extruder}
G1 X{new_x} Y{new_y} Z{new_z} F{travel_speed}
G1 E36 F5000
G92 E0
""", str, 'alteration', 'alteration')

setting('startMode', 'Simple', ['Simple', 'Normal'], 'preference', 'hidden')
setting('lastFile', os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'resources', 'example', 'UltimakerRobot_support.stl')), str, 'preference', 'hidden')
setting('machine_width', '205', float, 'preference', 'hidden')
setting('machine_depth', '205', float, 'preference', 'hidden')
setting('machine_height', '200', float, 'preference', 'hidden')
setting('machine_type', 'unknown', str, 'preference', 'hidden')
setting('machine_center_is_zero', 'False', bool, 'preference', 'hidden')
setting('ultimaker_extruder_upgrade', 'False', bool, 'preference', 'hidden')
setting('has_heated_bed', 'False', bool, 'preference', 'hidden')
setting('reprap_name', 'RepRap', str, 'preference', 'hidden')
setting('extruder_amount', '1', int, 'preference', 'hidden')
setting('extruder_offset_x1', '-21.6', float, 'preference', 'hidden')
setting('extruder_offset_y1', '0.0', float, 'preference', 'hidden')
setting('extruder_offset_x2', '0.0', float, 'preference', 'hidden')
setting('extruder_offset_y2', '0.0', float, 'preference', 'hidden')
setting('extruder_offset_x3', '0.0', float, 'preference', 'hidden')
setting('extruder_offset_y3', '0.0', float, 'preference', 'hidden')
setting('filament_physical_density', '1300', float, 'preference', 'hidden')
setting('steps_per_e', '0', float, 'preference', 'hidden')
setting('serial_port', 'AUTO', str, 'preference', 'hidden')
setting('serial_port_auto', '', str, 'preference', 'hidden')
setting('serial_baud', 'AUTO', str, 'preference', 'hidden')
setting('serial_baud_auto', '', int, 'preference', 'hidden')
setting('save_profile', 'False', bool, 'preference', 'hidden')
setting('filament_cost_kg', '0', float, 'preference', 'hidden')
setting('filament_cost_meter', '0', float, 'preference', 'hidden')
setting('sdpath', '', str, 'preference', 'hidden')
setting('sdshortnames', 'False', bool, 'preference', 'hidden')
setting('check_for_updates', 'True', bool, 'preference', 'hidden')
setting('submit_slice_information', 'False', bool, 'preference', 'hidden')

setting('planner_always_autoplace', 'True', bool, 'preference', 'hidden')
setting('extruder_head_size_min_x', '75.0', float, 'preference', 'hidden')
setting('extruder_head_size_min_y', '18.0', float, 'preference', 'hidden')
setting('extruder_head_size_max_x', '18.0', float, 'preference', 'hidden')
setting('extruder_head_size_max_y', '35.0', float, 'preference', 'hidden')
setting('extruder_head_size_height', '60.0', float, 'preference', 'hidden')

setting('model_colour', '#7AB645', str, 'preference', 'hidden')
setting('model_colour2', '#CB3030', str, 'preference', 'hidden')
setting('model_colour3', '#DDD93C', str, 'preference', 'hidden')
setting('model_colour4', '#4550D3', str, 'preference', 'hidden')

setting('window_maximized', 'False', bool, 'preference', 'hidden')
setting('window_pos_x', '-1', float, 'preference', 'hidden')
setting('window_pos_y', '-1', float, 'preference', 'hidden')
setting('window_width', '-1', float, 'preference', 'hidden')
setting('window_height', '-1', float, 'preference', 'hidden')
setting('window_normal_sash', '320', float, 'preference', 'hidden')

validators.warningAbove(settingsDictionary['layer_height'], lambda : (float(getProfileSetting('nozzle_size')) * 80.0 / 100.0), "Thicker layers then %.2fmm (80%% nozzle size) usually give bad results and are not recommended.")
validators.wallThicknessValidator(settingsDictionary['wall_thickness'])
validators.warningAbove(settingsDictionary['print_speed'], 150.0, "It is highly unlikely that your machine can achieve a printing speed above 150mm/s")
validators.printSpeedValidator(settingsDictionary['print_speed'])
validators.warningAbove(settingsDictionary['print_temperature'], 260.0, "Temperatures above 260C could damage your machine, be careful!")
validators.warningAbove(settingsDictionary['print_temperature2'], 260.0, "Temperatures above 260C could damage your machine, be careful!")
validators.warningAbove(settingsDictionary['print_temperature3'], 260.0, "Temperatures above 260C could damage your machine, be careful!")
validators.warningAbove(settingsDictionary['print_temperature4'], 260.0, "Temperatures above 260C could damage your machine, be careful!")
validators.warningAbove(settingsDictionary['filament_diameter'], 3.5, "Are you sure your filament is that thick? Normal filament is around 3mm or 1.75mm.")
validators.warningAbove(settingsDictionary['filament_diameter2'], 3.5, "Are you sure your filament is that thick? Normal filament is around 3mm or 1.75mm.")
validators.warningAbove(settingsDictionary['filament_diameter3'], 3.5, "Are you sure your filament is that thick? Normal filament is around 3mm or 1.75mm.")
validators.warningAbove(settingsDictionary['filament_diameter4'], 3.5, "Are you sure your filament is that thick? Normal filament is around 3mm or 1.75mm.")
validators.warningAbove(settingsDictionary['travel_speed'], 300.0, "It is highly unlikely that your machine can achieve a travel speed above 300mm/s")
validators.warningAbove(settingsDictionary['bottom_thickness'], lambda : (float(getProfileSetting('nozzle_size')) * 3.0 / 4.0), "A bottom layer of more then %.2fmm (3/4 nozzle size) usually give bad results and is not recommended.")

#Conditions for multiple extruders
settingsDictionary['print_temperature2'].addCondition(lambda : int(getPreference('extruder_amount')) > 1)
settingsDictionary['print_temperature3'].addCondition(lambda : int(getPreference('extruder_amount')) > 2)
settingsDictionary['print_temperature4'].addCondition(lambda : int(getPreference('extruder_amount')) > 3)
settingsDictionary['filament_diameter2'].addCondition(lambda : int(getPreference('extruder_amount')) > 1)
settingsDictionary['filament_diameter3'].addCondition(lambda : int(getPreference('extruder_amount')) > 2)
settingsDictionary['filament_diameter4'].addCondition(lambda : int(getPreference('extruder_amount')) > 3)
settingsDictionary['support_dual_extrusion'].addCondition(lambda : int(getPreference('extruder_amount')) > 1)
#Heated bed
settingsDictionary['print_bed_temperature'].addCondition(lambda : getPreference('has_heated_bed') == 'True')

#########################################################
## Profile and preferences functions
#########################################################

def getSubCategoriesFor(category):
	done = {}
	ret = []
	for s in settingsList:
		if s.getCategory() == category and not s.getSubCategory() in done:
			done[s.getSubCategory()] = True
			ret.append(s.getSubCategory())
	return ret

def getSettingsForCategory(category, subCategory = None):
	ret = []
	for s in settingsList:
		if s.getCategory() == category and (subCategory is None or s.getSubCategory() == subCategory):
			ret.append(s)
	return ret

## Profile functions
def getBasePath():
	if platform.system() == "Windows":
		basePath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
		#If we have a frozen python install, we need to step out of the library.zip
		if hasattr(sys, 'frozen'):
			basePath = os.path.normpath(os.path.join(basePath, ".."))
	else:
		basePath = os.path.expanduser('~/.cura/%s' % version.getVersion(False))
	if not os.path.isdir(basePath):
		os.makedirs(basePath)
	return basePath

def getDefaultProfilePath():
	return os.path.join(getBasePath(), 'current_profile.ini')

def loadProfile(filename):
	#Read a configuration file as global config
	profileParser = ConfigParser.ConfigParser()
	try:
		profileParser.read(filename)
	except ConfigParser.ParsingError:
		return
	global settingsList
	for set in settingsList:
		if set.isPreference():
			continue
		section = 'profile'
		if set.isAlteration():
			section = 'alterations'
		if profileParser.has_option(section, set.getName()):
			set.setValue(unicode(profileParser.get(section, set.getName()), 'utf-8', 'replace'))

def saveProfile(filename):
	#Save the current profile to an ini file
	profileParser = ConfigParser.ConfigParser()
	profileParser.add_section('profile')
	profileParser.add_section('alterations')
	global settingsList
	for set in settingsList:
		if set.isPreference():
			continue
		if set.isAlteration():
			profileParser.set('alterations', set.getName(), set.getValue().encode('utf-8'))
		else:
			profileParser.set('profile', set.getName(), set.getValue().encode('utf-8'))

	profileParser.write(open(filename, 'w'))

def resetProfile():
	#Read a configuration file as global config
	global settingsList
	for set in settingsList:
		if set.isPreference():
			continue
		set.setValue(set.getDefault())

	if getPreference('machine_type') == 'ultimaker':
		putProfileSetting('nozzle_size', '0.4')
		if getPreference('ultimaker_extruder_upgrade') == 'True':
			putProfileSetting('retraction_enable', 'True')
	else:
		putProfileSetting('nozzle_size', '0.5')

def loadProfileFromString(options):
	options = base64.b64decode(options)
	options = zlib.decompress(options)
	(profileOpts, alt) = options.split('\f', 1)
	global settingsDictionary
	for option in profileOpts.split('\b'):
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			if key in settingsDictionary:
				if settingsDictionary[key].isProfile():
					settingsDictionary[key].setValue(value)
	for option in alt.split('\b'):
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			if key in settingsDictionary:
				if settingsDictionary[key].isAlteration():
					settingsDictionary[key].setValue(value)

def getProfileString():
	p = []
	alt = []
	global settingsList
	for set in settingsList:
		if set.isProfile():
			if set.getName() in tempOverride:
				p.append(set.getName() + "=" + tempOverride[set.getName()])
			else:
				p.append(set.getName() + "=" + set.getValue())
		if set.isAlteration():
			if set.getName() in tempOverride:
				alt.append(set.getName() + "=" + tempOverride[set.getName()])
			else:
				alt.append(set.getName() + "=" + set.getValue())
	ret = '\b'.join(p) + '\f' + '\b'.join(alt)
	ret = base64.b64encode(zlib.compress(ret, 9))
	return ret

def getGlobalPreferencesString():
	p = []
	global settingsList
	for set in settingsList:
		if set.isPreference():
			p.append(set.getName() + "=" + set.getValue())
	ret = '\b'.join(p)
	ret = base64.b64encode(zlib.compress(ret, 9))
	return ret


def getProfileSetting(name):
	if name in tempOverride:
		return tempOverride[name]
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		return settingsDictionary[name].getValue()
	print 'Error: "%s" not found in profile settings' % (name)
	return ''

def getProfileSettingFloat(name):
	try:
		setting = getProfileSetting(name).replace(',', '.')
		return float(eval(setting, {}, {}))
	except (ValueError, SyntaxError, TypeError):
		return 0.0

def putProfileSetting(name, value):
	#Check if we have a configuration file loaded, else load the default.
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		settingsDictionary[name].setValue(value)

def isProfileSetting(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isProfile():
		return True
	return False

## Preferences functions
def getPreferencePath():
	return os.path.join(getBasePath(), 'preferences.ini')

def getPreferenceFloat(name):
	try:
		setting = getPreference(name).replace(',', '.')
		return float(eval(setting, {}, {}))
	except (ValueError, SyntaxError, TypeError):
		return 0.0

def getPreferenceColour(name):
	colorString = getPreference(name)
	return [float(int(colorString[1:3], 16)) / 255, float(int(colorString[3:5], 16)) / 255, float(int(colorString[5:7], 16)) / 255, 1.0]

def loadPreferences(filename):
	#Read a configuration file as global config
	profileParser = ConfigParser.ConfigParser()
	try:
		profileParser.read(filename)
	except ConfigParser.ParsingError:
		return
	global settingsList
	for set in settingsList:
		if set.isPreference():
			if profileParser.has_option('preferences', set.getName()):
				set.setValue(unicode(profileParser.get('preferences', set.getName()), 'utf-8', 'replace'))

def savePreferences(filename):
	#Save the current profile to an ini file
	parser = ConfigParser.ConfigParser()
	parser.add_section('preferences')
	global settingsList
	for set in settingsList:
		if set.isPreference():
			parser.set('preferences', set.getName(), set.getValue().encode('utf-8'))
	parser.write(open(filename, 'w'))

def getPreference(name):
	if name in tempOverride:
		return tempOverride[name]
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		return settingsDictionary[name].getValue()
	print 'Error: "%s" not found in profile settings' % (name)
	return ''

def putPreference(name, value):
	#Check if we have a configuration file loaded, else load the default.
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		settingsDictionary[name].setValue(value)
	savePreferences(getPreferencePath())

def isPreference(name):
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isPreference():
		return True
	return False

## Temp overrides for multi-extruder slicing and the project planner.
tempOverride = {}
def setTempOverride(name, value):
	tempOverride[name] = unicode(value).encode("utf-8")
def clearTempOverride(name):
	del tempOverride[name]
def resetTempOverride():
	tempOverride.clear()

#########################################################
## Utility functions to calculate common profile values
#########################################################
def calculateEdgeWidth():
	wallThickness = getProfileSettingFloat('wall_thickness')
	nozzleSize = getProfileSettingFloat('nozzle_size')
	
	if wallThickness < nozzleSize:
		return wallThickness

	lineCount = int(wallThickness / nozzleSize + 0.0001)
	lineWidth = wallThickness / lineCount
	lineWidthAlt = wallThickness / (lineCount + 1)
	if lineWidth > nozzleSize * 1.5:
		return lineWidthAlt
	return lineWidth

def calculateLineCount():
	wallThickness = getProfileSettingFloat('wall_thickness')
	nozzleSize = getProfileSettingFloat('nozzle_size')
	
	if wallThickness < nozzleSize:
		return 1

	lineCount = int(wallThickness / nozzleSize + 0.0001)
	lineWidth = wallThickness / lineCount
	lineWidthAlt = wallThickness / (lineCount + 1)
	if lineWidth > nozzleSize * 1.5:
		return lineCount + 1
	return lineCount

def calculateSolidLayerCount():
	layerHeight = getProfileSettingFloat('layer_height')
	solidThickness = getProfileSettingFloat('solid_layer_thickness')
	return int(math.ceil(solidThickness / layerHeight - 0.0001))

def getMachineCenterCoords():
	if getPreference('machine_center_is_zero') == 'True':
		return [0, 0]
	return [getPreferenceFloat('machine_width') / 2, getPreferenceFloat('machine_depth') / 2]

def getObjectMatrix():
	try:
		return map(float, getProfileSetting('model_matrix').split(','))
	except ValueError:
		return [1,0,0, 0,1,0, 0,0,1]


#########################################################
## Alteration file functions
#########################################################
def replaceTagMatch(m):
	pre = m.group(1)
	tag = m.group(2)
	if tag == 'time':
		return pre + time.strftime('%H:%M:%S').encode('utf-8', 'replace')
	if tag == 'date':
		return pre + time.strftime('%d %b %Y').encode('utf-8', 'replace')
	if tag == 'day':
		return pre + time.strftime('%a').encode('utf-8', 'replace')
	if tag == 'print_time':
		return pre + '#P_TIME#'
	if tag == 'filament_amount':
		return pre + '#F_AMNT#'
	if tag == 'filament_weight':
		return pre + '#F_WGHT#'
	if tag == 'filament_cost':
		return pre + '#F_COST#'
	if pre == 'F' and tag in ['print_speed', 'retraction_speed', 'travel_speed', 'max_z_speed', 'bottom_layer_speed', 'cool_min_feedrate']:
		f = getProfileSettingFloat(tag) * 60
	elif isProfileSetting(tag):
		f = getProfileSettingFloat(tag)
	elif isPreference(tag):
		f = getProfileSettingFloat(tag)
	else:
		return '%s?%s?' % (pre, tag)
	if (f % 1) == 0:
		return pre + str(int(f))
	return pre + str(f)

def replaceGCodeTags(filename, gcodeInt):
	f = open(filename, 'r+')
	data = f.read(2048)
	data = data.replace('#P_TIME#', ('%5d:%02d' % (int(gcodeInt.totalMoveTimeMinute / 60), int(gcodeInt.totalMoveTimeMinute % 60)))[-8:])
	data = data.replace('#F_AMNT#', ('%8.2f' % (gcodeInt.extrusionAmount / 1000))[-8:])
	data = data.replace('#F_WGHT#', ('%8.2f' % (gcodeInt.calculateWeight() * 1000))[-8:])
	cost = gcodeInt.calculateCost()
	if cost is None:
		cost = 'Unknown'
	data = data.replace('#F_COST#', ('%8s' % (cost.split(' ')[0]))[-8:])
	f.seek(0)
	f.write(data)
	f.close()

### Get aleration raw contents. (Used internally in Cura)
def getAlterationFile(filename):
	if filename in tempOverride:
		return tempOverride[filename]
	global settingsDictionary
	if filename in settingsDictionary and settingsDictionary[filename].isAlteration():
		return settingsDictionary[filename].getValue()
	print 'Error: "%s" not found in profile settings' % (filename)
	return ''

def setAlterationFile(name, value):
	#Check if we have a configuration file loaded, else load the default.
	global settingsDictionary
	if name in settingsDictionary and settingsDictionary[name].isAlteration():
		settingsDictionary[name].setValue(value)
	saveProfile(getDefaultProfilePath())

### Get the alteration file for output. (Used by Skeinforge)
def getAlterationFileContents(filename, extruderCount = 1):
	prefix = ''
	postfix = ''
	alterationContents = getAlterationFile(filename)
	if filename == 'start.gcode':
		#For the start code, hack the temperature and the steps per E value into it. So the temperature is reached before the start code extrusion.
		#We also set our steps per E here, if configured.
		eSteps = getPreferenceFloat('steps_per_e')
		if eSteps > 0:
			prefix += 'M92 E%f\n' % (eSteps)
		temp = getProfileSettingFloat('print_temperature')
		bedTemp = 0
		if getPreference('has_heated_bed') == 'True':
			bedTemp = getProfileSettingFloat('print_bed_temperature')
		
		if bedTemp > 0 and not '{print_bed_temperature}' in alterationContents:
			prefix += 'M140 S%f\n' % (bedTemp)
		if temp > 0 and not '{print_temperature}' in alterationContents:
			if extruderCount > 0:
				for n in xrange(1, extruderCount):
					t = temp
					if n > 0 and getProfileSettingFloat('print_temperature%d' % (n+1)) > 0:
						t = getProfileSettingFloat('print_temperature%d' % (n+1))
					prefix += 'M104 T%d S%f\n' % (n, temp)
				for n in xrange(0, extruderCount):
					t = temp
					if n > 0 and getProfileSettingFloat('print_temperature%d' % (n+1)) > 0:
						t = getProfileSettingFloat('print_temperature%d' % (n+1))
					prefix += 'M109 T%d S%f\n' % (n, temp)
				prefix += 'T0\n'
			else:
				prefix += 'M109 S%f\n' % (temp)
		if bedTemp > 0 and not '{print_bed_temperature}' in alterationContents:
			prefix += 'M190 S%f\n' % (bedTemp)
	elif filename == 'end.gcode':
		#Append the profile string to the end of the GCode, so we can load it from the GCode file later.
		postfix = ';CURA_PROFILE_STRING:%s\n' % (getProfileString())
	elif filename == 'replace.csv':
		#Always remove the extruder on/off M codes. These are no longer needed in 5D printing.
		prefix = 'M101\nM103\n'
	elif filename == 'support_start.gcode' or filename == 'support_end.gcode':
		#Add support start/end code 
		if getProfileSetting('support_dual_extrusion') == 'True' and int(getPreference('extruder_amount')) > 1:
			if filename == 'support_start.gcode':
				setTempOverride('extruder', '1')
			else:
				setTempOverride('extruder', '0')
			alterationContents = getAlterationFileContents('switchExtruder.gcode')
			clearTempOverride('extruder')
		else:
			alterationContents = ''
	return unicode(prefix + re.sub("(.)\{([^\}]*)\}", replaceTagMatch, alterationContents).rstrip() + '\n' + postfix).strip().encode('utf-8') + '\n'

###### PLUGIN #####

def getPluginConfig():
	try:
		return pickle.loads(getProfileSetting('plugin_config'))
	except:
		return []

def setPluginConfig(config):
	putProfileSetting('plugin_config', pickle.dumps(config))

def getPluginBasePaths():
	ret = []
	if platform.system() != "Windows":
		ret.append(os.path.expanduser('~/.cura/plugins/'))
	if platform.system() == "Darwin" and hasattr(sys, 'frozen'):
		ret.append(os.path.normpath(os.path.join(resources.resourceBasePath, "Cura/plugins")))
	else:
		ret.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'plugins')))
	return ret

def getPluginList():
	ret = []
	for basePath in getPluginBasePaths():
		for filename in glob.glob(os.path.join(basePath, '*.py')):
			filename = os.path.basename(filename)
			if filename.startswith('_'):
				continue
			with open(os.path.join(basePath, filename), "r") as f:
				item = {'filename': filename, 'name': None, 'info': None, 'type': None, 'params': []}
				for line in f:
					line = line.strip()
					if not line.startswith('#'):
						break
					line = line[1:].split(':', 1)
					if len(line) != 2:
						continue
					if line[0].upper() == 'NAME':
						item['name'] = line[1].strip()
					elif line[0].upper() == 'INFO':
						item['info'] = line[1].strip()
					elif line[0].upper() == 'TYPE':
						item['type'] = line[1].strip()
					elif line[0].upper() == 'DEPEND':
						pass
					elif line[0].upper() == 'PARAM':
						m = re.match('([a-zA-Z][a-zA-Z0-9_]*)\(([a-zA-Z_]*)(?::([^\)]*))?\) +(.*)', line[1].strip())
						if m is not None:
							item['params'].append({'name': m.group(1), 'type': m.group(2), 'default': m.group(3), 'description': m.group(4)})
					else:
						print "Unknown item in effect meta data: %s %s" % (line[0], line[1])
				if item['name'] != None and item['type'] == 'postprocess':
					ret.append(item)
	return ret

def runPostProcessingPlugins(gcodefilename):
	pluginConfigList = getPluginConfig()
	pluginList = getPluginList()
	
	for pluginConfig in pluginConfigList:
		plugin = None
		for pluginTest in pluginList:
			if pluginTest['filename'] == pluginConfig['filename']:
				plugin = pluginTest
		if plugin is None:
			continue
		
		pythonFile = None
		for basePath in getPluginBasePaths():
			testFilename = os.path.join(basePath, pluginConfig['filename'])
			if os.path.isfile(testFilename):
				pythonFile = testFilename
		if pythonFile is None:
			continue
		
		locals = {'filename': gcodefilename}
		for param in plugin['params']:
			value = param['default']
			if param['name'] in pluginConfig['params']:
				value = pluginConfig['params'][param['name']]
			
			if param['type'] == 'float':
				try:
					value = float(value)
				except:
					value = float(param['default'])
			
			locals[param['name']] = value
		try:
			execfile(pythonFile, locals)
		except:
			locationInfo = traceback.extract_tb(sys.exc_info()[2])[-1]
			return "%s: '%s' @ %s:%s:%d" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]), os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
	return None

def getSDcardDrives():
	drives = ['']
	if platform.system() == "Windows":
		from ctypes import windll
		bitmask = windll.kernel32.GetLogicalDrives()
		for letter in string.uppercase:
			if bitmask & 1:
				drives.append(letter + ':/')
			bitmask >>= 1
	if platform.system() == "Darwin":
		drives = []
		for volume in glob.glob('/Volumes/*'):
			if stat.S_ISLNK(os.lstat(volume).st_mode):
				continue
			drives.append(volume)
	return drives
