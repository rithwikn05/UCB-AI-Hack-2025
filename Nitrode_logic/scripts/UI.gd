# Clean minimal UI script matching current UI.tscn
extends CanvasLayer
class_name UI

# ------------------------------------------------------------------
# Signals
# ------------------------------------------------------------------
signal disaster_selected(disaster_name)
signal simulate_pressed(target_year, prompt)
signal image_clicked(position)
signal action_selected(action_name)

# ------------------------------------------------------------------
# Node references (cached in _ready)
# ------------------------------------------------------------------
var _selected_disaster := ""
var _current_year := 2024
var _disasters_placed := []
@onready var health_label : Label = find_child("HealthScoreLabel", true, false)
@onready var co2_label    : Label = find_child("CO2LevelLabel", true, false)

# UI Node refs - with null checking (match scene node names)
@onready var year_slider = find_child("YearSlider", true, false)
@onready var year_label = find_child("YearLabel", true, false)
@onready var main_image = find_child("MainImage", true, false)
@onready var disaster_buttons = find_child("DisasterButtons", true, false)
@onready var simulate_button = find_child("SimulateButton", true, false)
@onready var action_panel = find_child("ActionPanel", true, false)

func _ready():
	# These nodes are resolved via @onready; warn if any missing
	if year_label == null:
		push_error("YearLabel node not found!")
	if health_label == null:
		push_warning("HealthScoreLabel node not found – health stats will be hidden.")
	if co2_label == null:
		push_warning("CO2LevelLabel node not found – CO2 stats will be hidden.")
	if action_panel == null:
		push_warning("ActionPanel container not found – action buttons disabled.")

	# Connect every button under the action panel
	if action_panel:
		for btn in action_panel.get_children():
			if btn is Button:
				btn.pressed.connect(_on_action_button.bind(btn))

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
				button.pressed.connect(_on_disaster_button_pressed.bind(button))
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
	if is_instance_valid(year_label):
		year_label.text = str(_current_year)

func _on_disaster_button_pressed(btn: Button):
	# Prompt equals the button's text in lowercase
	var disaster_name := btn.text.strip_edges().to_lower()
	
	# Reset all button visuals
	for b in disaster_buttons.get_children():
		if b is Button:
			b.modulate = Color.WHITE
	
	# Toggle selection
	if _selected_disaster == disaster_name:
		_selected_disaster = ""
		btn.modulate = Color.WHITE
	else:
		_selected_disaster = disaster_name
		btn.modulate = Color.CYAN
	
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
	emit_signal("simulate_pressed", _current_year, _selected_disaster)

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
		button.pressed.connect(_on_disaster_button_pressed.bind(button))
		disaster_buttons.add_child(button)

func _on_action_button(btn: Button) -> void:
	var action_name := btn.text.strip_edges().to_lower()
	emit_signal("action_selected", action_name)

func update_stats(year: int, health: float, co2_ppm: float) -> void:
	if year_label:
		year_label.text = "Year: %d" % year
	if health_label:
		health_label.text = "Health: %.1f" % health
	if co2_label:
		co2_label.text = "CO2: %.1f ppm" % co2_ppm

func set_action_buttons(names: Array[String]) -> void:
	if action_panel == null:
		return
	# Remove old buttons
	for child in action_panel.get_children():
		child.queue_free()
	# Add new ones
	for n in names:
		var b := Button.new()
		b.text = n.capitalize()
		b.pressed.connect(_on_action_button.bind(b))
		action_panel.add_child(b)
