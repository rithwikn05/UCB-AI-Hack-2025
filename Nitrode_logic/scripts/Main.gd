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
    world.update_tile_image(tile_index, new_texture)

func _on_tile_state_changed(tile_index, new_label):
    api_manager.request_tile_image(tile_index, new_label)

func _on_year_advanced(new_year):
    if ui.has_method("update_stats"):
        ui.update_stats(new_year, get_node("/root/GameStateManager").global_health_score, get_node("/root/GameStateManager").co2_level) 