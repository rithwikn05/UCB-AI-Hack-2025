extends Node

@onready var world = get_node("World") if has_node("World") else null
@onready var ui = get_node("UI") if has_node("UI") else null  
@onready var api_manager = get_node("APIManager") if has_node("APIManager") else null

#Path to the initial image (can be changed to a file dialog or API call)
var initial_image_path = "res://assets/Ea3mbccg.jpg"
var _selected_tile := -1

func _ready():
	# Check if nodes exist before connecting
	if world == null:
		push_error("World node not found!")
		return
	if ui == null:
		push_error("UI node not found!")
		return
	if api_manager == null:
		push_error("APIManager node not found!")
		return
	
	# Connect signals between subsystems
	# Note: Using the new signal names from the updated files
	if ui.has_signal("disaster_selected"):
		ui.disaster_selected.connect(_on_disaster_selected)
	if ui.has_signal("simulate_pressed"):
		ui.simulate_pressed.connect(_on_simulate_pressed)
	if ui.has_signal("image_clicked"):
		ui.image_clicked.connect(_on_image_clicked)
	if api_manager.has_signal("image_generated"):
		api_manager.image_generated.connect(_on_image_generated)
	
	# Connect to GameStateManager if it exists
	if has_node("/root/GameStateManager"):
		var gsm = get_node("/root/GameStateManager")
		if gsm.has_signal("tile_state_changed"):
			gsm.tile_state_changed.connect(_on_tile_state_changed)
		if gsm.has_signal("year_advanced"):
			gsm.year_advanced.connect(_on_year_advanced)
	
	# Load and display the initial image
	_load_initial_image()

func _load_initial_image():
	if FileAccess.file_exists(initial_image_path):
		var tex = load(initial_image_path)
		if tex and ui.has_method("set_main_image"):
			ui.set_main_image(tex)
	else:
		print("Initial image not found at: ", initial_image_path)

# New signal handlers for the updated UI system
func _on_disaster_selected(disaster_name: String):
	print("Disaster selected: ", disaster_name)

func _on_simulate_pressed(target_year: int):
	print("Simulate pressed for year: ", target_year)
	if ui.has_method("get_main_image_data") and ui.has_method("get_disasters_data"):
		var image_data = ui.get_main_image_data()
		var disasters = ui.get_disasters_data()
		if image_data != null:
			api_manager.simulate_climate_change(image_data, disasters, target_year)

func _on_image_clicked(position: Vector2):
	print("Image clicked at position: ", position)

func _on_image_generated(tile_index, new_texture):
	if ui.has_method("set_main_image"):
		ui.set_main_image(new_texture)

# Legacy handlers for GameStateManager compatibility
func _on_tile_state_changed(tile_index, new_label):
	if api_manager.has_method("request_tile_image"):
		api_manager.request_tile_image(tile_index, new_label)

func _on_year_advanced(new_year):
	if ui.has_method("update_stats") and has_node("/root/GameStateManager"):
		var gsm = get_node("/root/GameStateManager")
		ui.update_stats(new_year, gsm.global_health_score, gsm.co2_level)


# extends Node
# # class_name Main

# @onready var world = $World
# @onready var ui = $UI
# @onready var api_manager = $APIManager

# # Path to the initial image (can be changed to a file dialog or API call)
# var initial_image_path = "res://assets/initial_image.png"

# var _selected_tile := -1

# func _ready():
#     # Connect signals between subsystems
#     world.tile_clicked.connect(_on_tile_clicked)
#     ui.action_selected.connect(_on_action_selected)
#     api_manager.image_generated.connect(_on_image_generated)
#     get_node("/root/GameStateManager").tile_state_changed.connect(_on_tile_state_changed)
#     get_node("/root/GameStateManager").year_advanced.connect(_on_year_advanced)
#     # Load and display the initial image
#     # _load_initial_image()

# func _load_initial_image():
#     var tex = load(initial_image_path)
#     if tex and world.has_method("set_main_image"):
#         world.set_main_image(tex)

# func _on_tile_clicked(tile_index):
#     _selected_tile = tile_index
#     if ui.has_method("set_selected_tile"):
#         ui.set_selected_tile(tile_index)

# func _on_action_selected(action_name, _tile_index):
#     if _selected_tile == -1:
#         push_warning("No tile selected!")
#         return
#     get_node("/root/GameStateManager").apply_action(action_name, _selected_tile)

# func _on_image_generated(tile_index, new_texture):
#     world.update_tile_image(tile_index, new_texture)

# func _on_tile_state_changed(tile_index, new_label):
#     api_manager.request_tile_image(tile_index, new_label)

# func _on_year_advanced(new_year):
#     if ui.has_method("update_stats"):
#         ui.update_stats(new_year, get_node("/root/GameStateManager").global_health_score, get_node("/root/GameStateManager").co2_level) 