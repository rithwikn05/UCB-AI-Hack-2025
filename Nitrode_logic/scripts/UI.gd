extends CanvasLayer
class_name UI

signal action_selected(action_name, tile_index)

var _selected_tile := -1

#--- UI Node refs -----------------------------------------------------------
@onready var year_label   = get_node("YearLabel")
@onready var health_label = get_node("HealthScoreLabel")
@onready var co2_label    = get_node("CO2LevelLabel")
@onready var action_panel = get_node("HBoxContainer")

func _ready():
	# Automatically connect any Button under ActionPanel whose name ends with "Button"
	for button in action_panel.get_children():
		if button is Button:
			button.pressed.connect(_on_action_button_pressed.bind(button.name))

func _on_action_button_pressed(button_name: String):
	if _selected_tile == -1:
		return
	var action_name := button_name.substr(0, button_name.length() - 6).to_lower() # Strip "Button"
	emit_signal("action_selected", action_name, _selected_tile)

# Legacy example button kept for clarity
func _on_ReforestButton_pressed():
	if _selected_tile == -1:
		return
	emit_signal("action_selected", "reforest", _selected_tile)

func set_selected_tile(tile_index):
	_selected_tile = tile_index

func update_stats(year: int, health: float, co2: float):
	if is_instance_valid(year_label):
		year_label.text = "Year: %d" % year
	if is_instance_valid(health_label):
		health_label.text = "Health: %.1f" % health
	if is_instance_valid(co2_label):
		co2_label.text = "CO2: %.1f ppm" % co2 
