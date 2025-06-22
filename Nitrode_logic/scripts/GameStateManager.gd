extends Node

# Emits when the in-game year changes.
signal year_advanced(new_year)
# Emits when a tile receives a new semantic label (before an image is generated).
signal tile_state_changed(tile_index, new_label)

# -------- Public State -------- #
var current_year: int = 0
var max_years: int = 50

var global_health_score: float = 100.0
var co2_level: float = 400.0 # ppm – baseline value

# Each tile stores a dictionary like:
# Example tile record: {"label": "healthy_forest", "modifiers": []}
var tile_data = []

# Size of the square grid that makes up the world.
# NOTE: Update this if you change your world size in the World scene.
@export var grid_size: int = 10

func _ready() -> void:
    _init_tiles()

func _init_tiles() -> void:
    tile_data.clear()
    for _i in range(grid_size * grid_size):
        tile_data.append({
            "label": "healthy_forest",
            "modifiers": []
        })

# --- Gameplay API ----------------------------------------------------------

func apply_action(action_name: String, tile_index: int) -> void:
    # Safety checks
    if tile_index < 0 or tile_index >= tile_data.size():
        push_warning("[GameStateManager] Invalid tile index %d" % tile_index)
        return

    var tile := tile_data[tile_index] as Dictionary
    tile["modifiers"].append(action_name)

    # Produce a new semantic label that will be fed to the diffusion model.
    var new_label := _build_label(tile, action_name)
    tile["label"] = new_label

    # Persist changes
    tile_data[tile_index] = tile

    emit_signal("tile_state_changed", tile_index, new_label)

func advance_year() -> void:
    current_year += 1
    emit_signal("year_advanced", current_year)
    # TODO: Add logic that updates global stats (health, CO2, etc.)

# --- Helpers ---------------------------------------------------------------

func _build_label(tile: Dictionary, action_name: String) -> String:
    # Very naive implementation – replace with a smarter label generator.
    var base_label: String = tile.get("label", "land")
    return "%s_after_%s_year_%d" % [base_label, action_name, current_year] 