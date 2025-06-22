import replicate

prompt = "fire"
input = {
    "prompt": "an ariel view of a landscape that has been affected by {prompt}. Make it zoom out and realistic.",
    "scheduler": "K_EULER"
}

output = replicate.run(
    "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
    input=input
)
for index, item in enumerate(output):
    with open(f"output_{index}.png", "wb") as file:
        file.write(item.read())

print(prompt)
#=> output_0.png written to disk