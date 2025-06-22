extends Control
# class_name World

signal tile_clicked(tile_index)

@export var grid_size: int = 10
@export var placeholder_texture: Texture2D

@onready var grid_container = $GridContainer
var _tiles = []
@onready var main_image = $MainImage if has_node("MainImage") else null

func _ready():
	_build_grid()

func _build_grid():
	_tiles.clear()
	grid_container.columns = grid_size
	var tile_size := Vector2(64, 64)
	for i in range(grid_size * grid_size):
		var tile := TextureRect.new()
		tile.name = "Tile%d" % i
		tile.expand = true
		tile.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		# tile.rect_min_size = tile_size
		tile.custom_minimum_size = tile_size
		tile.texture = placeholder_texture
		tile.mouse_filter = Control.MOUSE_FILTER_PASS
		tile.gui_input.connect(func(event): _on_tile_gui_input(event, i))
		grid_container.add_child(tile)
		_tiles.append(tile)

func _on_tile_gui_input(event, tile_index):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		emit_signal("tile_clicked", tile_index)

func update_tile_image(tile_index, texture):
	if tile_index < 0 or tile_index >= _tiles.size():
		push_warning("[World] Invalid tile index %d" % tile_index)
		return
	_tiles[tile_index].texture = texture 

func set_main_image(tex):
	if main_image:
		main_image.texture = tex

func get_main_image_data():
	if main_image and main_image.texture:
		var img = main_image.texture.get_image()
		img.flip_y() # Godot images are flipped vertically
		return img.save_png_to_buffer()
	return null 
