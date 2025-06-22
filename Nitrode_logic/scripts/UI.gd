extends CanvasLayer
class_name UI

signal disaster_selected(disaster_name)
signal simulate_pressed(target_year)
signal image_clicked(position)

var _selected_disaster := ""
var _current_year := 2024
var _disasters_placed := []

# UI Node refs - with null checking
@onready var year_label = find_child("YearLabel", true, false)
@onready var year_slider = find_child("YearSlider", true, false) 
@onready var year_display = find_child("YearDisplay", true, false)
@onready var main_image = find_child("MainImage", true, false)
@onready var disaster_buttons = find_child("DisasterButtons", true, false)
@onready var simulate_button = find_child("SimulateButton", true, false)

func _ready():
	# Debug: Print what children we actually have
	print("UI children found:")
	print("  year_slider: ", year_slider)
	print("  main_image: ", main_image)
	print("  disaster_buttons: ", disaster_buttons)
	print("  simulate_button: ", simulate_button)
	
	# Setup year slider with null check
	if year_slider != null:
		year_slider.min_value = 2020
		year_slider.max_value = 2100
		year_slider.value = _current_year
		year_slider.value_changed.connect(_on_year_slider_changed)
	else:
		push_error("YearSlider node not found!")
	
	# Setup disaster buttons with null check
	if disaster_buttons != null:
		for button in disaster_buttons.get_children():
			if button is Button:
				button.pressed.connect(_on_disaster_button_pressed.bind(button.name))
	else:
		push_error("DisasterButtons container not found!")
	
	# Setup simulate button with null check
	if simulate_button != null:
		simulate_button.pressed.connect(_on_simulate_button_pressed)
	else:
		push_error("SimulateButton not found!")
	
	# Setup main image click detection with null check
	if main_image != null:
		main_image.gui_input.connect(_on_main_image_gui_input)
	else:
		push_error("MainImage not found!")
	
	_update_year_display()

func _on_year_slider_changed(value):
	_current_year = int(value)
	_update_year_display()

func _update_year_display():
	if is_instance_valid(year_display):
		year_display.text = str(_current_year)

func _on_disaster_button_pressed(button_name: String):
	# Toggle disaster selection
	var disaster_name = button_name.replace("Button", "").to_lower()
	
	# Reset all button states
	for button in disaster_buttons.get_children():
		if button is Button:
			button.modulate = Color.WHITE
	
	# Highlight selected button
	var pressed_button = disaster_buttons.get_node(button_name)
	if _selected_disaster == disaster_name:
		_selected_disaster = ""
		pressed_button.modulate = Color.WHITE
	else:
		_selected_disaster = disaster_name
		pressed_button.modulate = Color.CYAN
	
	emit_signal("disaster_selected", _selected_disaster)

func _on_main_image_gui_input(event):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		if _selected_disaster != "":
			var click_pos = event.position
			_place_disaster(click_pos)
			emit_signal("image_clicked", click_pos)

func _place_disaster(position: Vector2):
	if _selected_disaster == "":
		return
	
	# Create disaster marker
	var marker = ColorRect.new()
	marker.size = Vector2(10, 10)
	marker.color = Color.RED
	marker.position = position - marker.size / 2
	main_image.add_child(marker)
	
	# Store disaster data
	_disasters_placed.append({
		"type": _selected_disaster,
		"position": position,
		"year": _current_year
	})

func _on_simulate_button_pressed():
	emit_signal("simulate_pressed", _current_year)

func set_main_image(texture: Texture2D):
	if is_instance_valid(main_image):
		main_image.texture = texture

func get_main_image_data():
	if main_image and main_image.texture:
		var img = main_image.texture.get_image()
		return img.save_png_to_buffer()
	return null

func get_disasters_data():
	return _disasters_placed

func clear_disasters():
	_disasters_placed.clear()
	# Remove visual markers
	for child in main_image.get_children():
		if child is ColorRect:
			child.queue_free()

func update_disaster_buttons(button_names: Array):
	# Clear existing buttons
	for child in disaster_buttons.get_children():
		child.queue_free()
	
	# Create new buttons
	for name in button_names:
		var button = Button.new()
		button.name = name + "Button"
		button.text = name.capitalize()
		button.pressed.connect(_on_disaster_button_pressed.bind(button.name))
		disaster_buttons.add_child(button)


# extends CanvasLayer
# class_name UI

# signal action_selected(action_name, tile_index)

# var _selected_tile := -1

# #--- UI Node refs -----------------------------------------------------------
# @onready var year_label   = get_node("YearLabel")
# @onready var health_label = get_node("HealthScoreLabel")
# @onready var co2_label    = get_node("CO2LevelLabel")
# @onready var action_panel = get_node("HBoxContainer")

# func _ready():
# 	# Automatically connect any Button under ActionPanel whose name ends with "Button"
# 	for button in action_panel.get_children():
# 		if button is Button:
# 			button.pressed.connect(_on_action_button_pressed.bind(button.name))

# func _on_action_button_pressed(button_name: String):
# 	if _selected_tile == -1:
# 		return
# 	var action_name := button_name.substr(0, button_name.length() - 6).to_lower() # Strip "Button"
# 	emit_signal("action_selected", action_name, _selected_tile)

# # Legacy example button kept for clarity
# func _on_ReforestButton_pressed():
# 	if _selected_tile == -1:
# 		return
# 	emit_signal("action_selected", "reforest", _selected_tile)

# func set_selected_tile(tile_index):
# 	_selected_tile = tile_index

# func update_stats(year: int, health: float, co2: float):
# 	if is_instance_valid(year_label):
# 		year_label.text = "Year: %d" % year
# 	if is_instance_valid(health_label):
# 		health_label.text = "Health: %.1f" % health
# 	if is_instance_valid(co2_label):
# 		co2_label.text = "CO2: %.1f ppm" % co2 
