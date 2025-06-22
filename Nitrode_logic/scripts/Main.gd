# extends CanvasLayer

# @onready var world = get_node("World") if has_node("World") else null
# @onready var ui = get_node("UI") if has_node("UI") else null  
# @onready var api_manager = get_node("APIManager") if has_node("APIManager") else null

# @onready var year_slider : HSlider = %YearSlider
# @onready var image_rect  : TextureRect = %ImageRect
# @onready var simulate_btn: Button     = %Simulate
# @onready var disaster_buttons := [%Btn1, %Btn2, %Btn3, %Btn4]

# var active_tool : String = ""    # which "disaster" we're painting

# #Path to the initial image (can be changed to a file dialog or API call)
# var initial_image_path = "res://assets/Ea3mbccg.jpg"
# var _selected_tile := -1

# func _ready():
# 	# Check if nodes exist before connecting
# 	if world == null:
# 		push_error("World node not found!")
# 		return
# 	if ui == null:
# 		push_error("UI node not found!")
# 		return
# 	if api_manager == null:
# 		push_error("APIManager node not found!")
# 		return
	
# 	# Connect signals between subsystems
# 	# Note: Using the new signal names from the updated files
# 	if ui.has_signal("disaster_selected"):
# 		ui.disaster_selected.connect(_on_disaster_selected)
# 	if ui.has_signal("simulate_pressed"):
# 		ui.simulate_pressed.connect(_on_simulate_pressed)
# 	if ui.has_signal("image_clicked"):
# 		ui.image_clicked.connect(_on_image_clicked)
# 	if api_manager.has_signal("image_generated"):
# 		api_manager.image_generated.connect(_on_image_generated)
	
# 	# Connect to GameStateManager if it exists
# 	if has_node("/root/GameStateManager"):
# 		var gsm = get_node("/root/GameStateManager")
# 		if gsm.has_signal("tile_state_changed"):
# 			gsm.tile_state_changed.connect(_on_tile_state_changed)
# 		if gsm.has_signal("year_advanced"):
# 			gsm.year_advanced.connect(_on_year_advanced)
	
# 	# Load and display the initial image
# 	_load_initial_image()

# 	# give each disaster button its own pressed handler
# 	for btn in disaster_buttons:
# 		btn.pressed.connect(_on_disaster_selected.bind(btn))
# 	simulate_btn.pressed.connect(_on_simulate)
# 	year_slider.value_changed.connect(_on_year_changed)

# func _load_initial_image():
# 	if FileAccess.file_exists(initial_image_path):
# 		var tex = load(initial_image_path)
# 		if tex and ui.has_method("set_main_image"):
# 			ui.set_main_image(tex)
# 	else:
# 		print("Initial image not found at: ", initial_image_path)

# # New signal handlers for the updated UI system
# func _on_disaster_selected(btn: Button) -> void:
# 	active_tool = btn.text
# 	for b in disaster_buttons:
# 		b.toggle_mode = true
# 		b.button_pressed = (b == btn)
# 	print("Selected tool:", active_tool)

# func _on_simulate_pressed(target_year: int):
# 	print("Simulate pressed for year: ", target_year)
# 	if ui.has_method("get_main_image_data") and ui.has_method("get_disasters_data"):
# 		var image_data = ui.get_main_image_data()
# 		var disasters = ui.get_disasters_data()
# 		if image_data != null:
# 			api_manager.simulate_climate_change(image_data, disasters, target_year)

# func _on_image_clicked(position: Vector2):
# 	print("Image clicked at position: ", position)

# func _on_image_generated(tile_index, new_texture):
# 	# If tile_index is 0 coming from Simulate, show it in the main UI.
# 	if tile_index == 0:
# 		ui.set_main_image(new_texture)
# 	else:
# 		world.update_tile_image(tile_index, new_texture)

# # Legacy handlers for GameStateManager compatibility
# func _on_tile_state_changed(tile_index, new_label):
# 	if api_manager.has_method("request_tile_image"):
# 		api_manager.request_tile_image(tile_index, new_label)

# func _on_year_advanced(new_year):
# 	if ui.has_method("update_stats") and has_node("/root/GameStateManager"):
# 		var gsm = get_node("/root/GameStateManager")
# 		ui.update_stats(new_year, gsm.global_health_score, gsm.co2_level)

# func _unhandled_input(event: InputEvent) -> void:
# 	if event is InputEventMouseButton and event.pressed and active_tool != "":
# 		var pos = event.position - image_rect.global_position
# 		if Rect2(Vector2.ZERO, image_rect.size).has_point(pos):
# 			_place_marker(pos / image_rect.size)
# 			event.consume()

# func _place_marker(uv: Vector2) -> void:
# 	# uv is 0–1 coordinates inside the image
# 	print("Placed", active_tool, "at", uv)
# 	# Emit a signal here if other scripts need to know
# 	# or queue for REST submission.

# func _on_year_changed(new_val: float) -> void:
# 	print("Target year:", int(new_val))

# func _on_simulate() -> void:
# 	print("Simulating", active_tool, "objects until year", int(year_slider.value))
# 	# TODO: call your REST API, then replace image:
# 	# image_rect.texture = new_texture

extends Node
# class_name Main

@onready var world = $World
@onready var ui = $UI
@onready var api_manager = $APIManager

# Path to the initial image (can be changed to a file dialog or API call)
var initial_image_path = "res://assets/initial_image.png"

var _selected_tile := -1

func _ready():
	# Connect signals between subsystems
	world.tile_clicked.connect(_on_tile_clicked)
	ui.action_selected.connect(_on_action_selected)
	ui.simulate_pressed.connect(_on_simulate_pressed)
	api_manager.image_generated.connect(_on_image_generated)
	get_node("/root/GameStateManager").tile_state_changed.connect(_on_tile_state_changed)
	get_node("/root/GameStateManager").year_advanced.connect(_on_year_advanced)
	# Load and display the initial image
	# _load_initial_image()

func _load_initial_image():
	var tex = load(initial_image_path)
	if tex and world.has_method("set_main_image"):
		world.set_main_image(tex)

func _on_tile_clicked(tile_index):
	_selected_tile = tile_index
	if ui.has_method("set_selected_tile"):
		ui.set_selected_tile(tile_index)

func _on_action_selected(action_name, _tile_index):
	if _selected_tile == -1:
		push_warning("No tile selected!")
		return
	get_node("/root/GameStateManager").apply_action(action_name, _selected_tile)

func _on_image_generated(tile_index, new_texture):
	# If tile_index is 0 coming from Simulate, show it in the main UI.
	if tile_index == 0:
		ui.set_main_image(new_texture)
	else:
		world.update_tile_image(tile_index, new_texture)
		print("[Main] image_received tile=", tile_index, "tex=", new_texture)

func _on_tile_state_changed(tile_index, new_label):
	api_manager.request_tile_image(tile_index, new_label)

func _on_year_advanced(new_year):
	if ui.has_method("update_stats"):
		ui.update_stats(new_year, get_node("/root/GameStateManager").global_health_score, get_node("/root/GameStateManager").co2_level) 

func _on_simulate_pressed(year:int, prompt:String) -> void:
	if prompt == "":
		push_warning("No disaster selected")
		return
	# tile_index isn't used on the stub – send 0
	print("[Main] sending prompt ->", prompt)
	api_manager.request_tile_image(0, prompt)

#func _on_image_generated(_tile_index:int, tex:Texture2D) -> void:
	#ui.set_main_image(tex)    # instantly swap the big image 

func _on_simulate_button_pressed():
	print("[UI] simulate_pressed year=%d prompt=%s" %
		  [_current_year, _selected_disaster])
	emit_signal("simulate_pressed", _current_year, _selected_disaster)
