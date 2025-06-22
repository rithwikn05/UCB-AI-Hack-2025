# extends Node

# signal image_generated(tile_index, texture)

# @export var api_url: String = "http://localhost:8000/generate"

# var _http_request: HTTPRequest

# func _ready() -> void:
# 	_http_request = HTTPRequest.new()
# 	add_child(_http_request)
# 	_http_request.request_completed.connect(_on_request_completed)

# func request_tile_image(tile_index, label):
# 	var headers = ["Content-Type: application/json"]
# 	var payload = {
# 		"tile_index": tile_index,
# 		"label": label
# 	}
# 	var json_payload = JSON.stringify(payload)
# 	var err = _http_request.request(api_url, headers, HTTPClient.METHOD_POST, json_payload)
# 	if err != OK:
# 		push_warning("[APIManager] Failed to send request: %s" % err)

# func request_image_modification(image_data, action_name, year: int):
# 	var headers = ["Content-Type: application/json"]
# 	var payload = {
# 		"image": Marshalls.raw_to_base64(image_data),
# 		"action": action_name,
# 		"year": year
# 	}
# 	var json_payload = JSON.stringify(payload)
# 	var err = _http_request.request(api_url, headers, HTTPClient.METHOD_POST, json_payload)
# 	if err != OK:
# 		push_warning("[APIManager] Failed to send request: %s" % err)

# func simulate_climate_change(image_data, disasters: Array, target_year: int):
# 	var headers = ["Content-Type: application/json"]
# 	var payload = {
# 		"image": Marshalls.raw_to_base64(image_data),
# 		"disasters": disasters,
# 		"target_year": target_year
# 	}
# 	var json_payload = JSON.stringify(payload)
# 	var err = _http_request.request(api_url, headers, HTTPClient.METHOD_POST, json_payload)
# 	if err != OK:
# 		push_warning("[APIManager] Failed to send simulation request: %s" % err)

# func _on_request_completed(result, response_code, _headers, body):
# 	if response_code != 200:
# 		push_warning("[APIManager] Bad response code: %d" % response_code)
# 		return
	
# 	var json = JSON.new()
# 	var parse_err = json.parse(body.get_string_from_utf8())
# 	if parse_err != OK:
# 		push_warning("[APIManager] Failed to parse JSON: %s" % parse_err)
# 		return
	
# 	var data = json.data
# 	if not data.has("image"):
# 		push_warning("[APIManager] JSON missing image key")
# 		return
	
# 	var raw_bytes = Marshalls.base64_to_raw(data["image"])
# 	var img = Image.new()
# 	var img_err = img.load_png_from_buffer(raw_bytes)
# 	if img_err != OK:
# 		push_warning("[APIManager] Failed to decode PNG buffer: %s" % img_err)
# 		return
	
# 	var tex = ImageTexture.create_from_image(img)
# 	emit_signal("image_generated", -1, tex)


extends Node
# class_name APIManager

signal image_generated(tile_index, texture)

# --- Settings -------------------------------------------------------------
# Update this to your backend endpoint.
@export var api_url: String = "http://localhost:8000/generate"

# --- Internal -------------------------------------------------------------
var _http_request: HTTPRequest

func _ready() -> void:
	# Create an HTTPRequest node dynamically so this script can work even if
	# you forget to add one in the editor.
	_http_request = HTTPRequest.new()
	add_child(_http_request)
	_http_request.request_completed.connect(_on_request_completed)

func request_tile_image(tile_index, label):
	var headers = ["Content-Type: application/json"]
	var payload = {
		"tile_index": tile_index,
		"label": label
	}
	var json_payload = JSON.stringify(payload)
	var err = _http_request.request(api_url, headers, HTTPClient.METHOD_POST, json_payload)
	if err != OK:
		push_warning("[APIManager] Failed to send request: %s" % err)

func request_image_modification(image_data, action_name):
	var headers = ["Content-Type: application/json"]
	var payload = {
		"image": Marshalls.raw_to_base64(image_data),
		"action": action_name
	}
	var json_payload = JSON.stringify(payload)
	var err = _http_request.request(api_url, headers, HTTPClient.METHOD_POST, json_payload)
	if err != OK:
		push_warning("[APIManager] Failed to send request: %s" % err)

func _on_request_completed(result, response_code, _headers, body):
	if response_code != 200:
		push_warning("[APIManager] Bad response code: %d" % response_code)
		return
	var json = JSON.new()
	var parse_err = json.parse(body.get_string_from_utf8())
	if parse_err != OK:
		push_warning("[APIManager] Failed to parse JSON: %s" % parse_err)
		return
	var data = json.data
	if not data.has("image") or not data.has("tile_index"):
		push_warning("[APIManager] JSON missing keys")
		return
	var raw_bytes = Marshalls.base64_to_raw(data["image"])
	var img = Image.new()
	var img_err = img.load_png_from_buffer(raw_bytes)
	if img_err != OK:
		push_warning("[APIManager] Failed to decode PNG buffer: %s" % img_err)
		return
	var tex = ImageTexture.create_from_image(img)
	emit_signal("image_generated", data["tile_index"], tex)
	print("[APIManager] HTTP code =", response_code) 
