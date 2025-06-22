# extends Control

# @onready var ui = get_node("UI") if has_node("UI") else null
# @onready var api_manager = get_node("APIManager") if has_node("APIManager") else null

# var _current_image_data = null

# func _ready():
# 	# Check if nodes exist before connecting
# 	if ui == null:
# 		push_error("UI node not found! Make sure you have a UI node as a child of this Control node.")
# 		return
		
# 	if api_manager == null:
# 		push_error("APIManager node not found! Make sure you have an APIManager node as a child of this Control node.")
# 		return
	
# 	# Connect UI signals
# 	ui.disaster_selected.connect(_on_disaster_selected)
# 	ui.simulate_pressed.connect(_on_simulate_pressed)
# 	ui.image_clicked.connect(_on_image_clicked)
	
# 	# Connect API signals
# 	api_manager.image_generated.connect(_on_image_generated)
	
# 	# Setup file dialog for loading images
# 	var file_dialog = FileDialog.new()
# 	file_dialog.file_mode = FileDialog.FILE_MODE_OPEN_FILE
# 	file_dialog.access = FileDialog.ACCESS_FILESYSTEM
# 	file_dialog.add_filter("*.png", "PNG Images")
# 	file_dialog.add_filter("*.jpg", "JPEG Images")
# 	file_dialog.file_selected.connect(_on_image_file_selected)
# 	add_child(file_dialog)
	
# 	# For testing - you can remove this
# 	_load_placeholder_image()

# func _load_placeholder_image():
# 	# Create a simple placeholder image
# 	var img = Image.create(512, 512, false, Image.FORMAT_RGB8)
# 	img.fill(Color(0.2, 0.4, 0.2))  # Dark green for forest
# 	var texture = ImageTexture.create_from_image(img)
# 	ui.set_main_image(texture)
# 	_current_image_data = img.save_png_to_buffer()

# func _on_disaster_selected(disaster_name: String):
# 	print("Selected disaster: ", disaster_name)

# func _on_image_clicked(position: Vector2):
# 	print("Placed disaster at: ", position)

# func _on_simulate_pressed(target_year: int):
# 	if _current_image_data == null:
# 		push_warning("No image loaded for simulation")
# 		return
	
# 	var disasters = ui.get_disasters_data()
# 	print("Simulating to year ", target_year, " with ", disasters.size(), " disasters")
	
# 	# Send to API
# 	api_manager.simulate_climate_change(_current_image_data, disasters, target_year)

# func _on_image_generated(tile_index, texture):
# 	# Update main image with simulated result
# 	ui.set_main_image(texture)
	
# 	# Update stored image data
# 	var img = texture.get_image()
# 	_current_image_data = img.save_png_to_buffer()

# func _on_image_file_selected(path: String):
# 	var img = Image.new()
# 	var err = img.load(path)
# 	if err != OK:
# 		push_warning("Failed to load image: " + path)
# 		return
	
# 	var texture = ImageTexture.create_from_image(img)
# 	ui.set_main_image(texture)
# 	_current_image_data = img.save_png_to_buffer()
	
# 	# Clear any existing disasters
# 	ui.clear_disasters()

# # Method to update disaster button names from API
# func update_disaster_options(options: Array):
# 	ui.update_disaster_buttons(options)


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
