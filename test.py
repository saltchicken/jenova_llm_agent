from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("stabilityai/stablecode-completion-alpha-3b-4k")
model = AutoModelForCausalLM.from_pretrained(
  "stabilityai/stablecode-completion-alpha-3b-4k",
  # trust_remote_code=True,
  torch_dtype="auto",
)
model.cuda()
input_text = "class NewClass():\n   def __"
inputs = tokenizer(input_text, return_tensors="pt").to("cuda")
del inputs["token_type_ids"]
tokens = model.generate(
  **inputs,
  max_new_tokens=48,
  temperature=0.2,
  do_sample=True,
)
prediction = tokenizer.decode(tokens[0], skip_special_tokens=True) 
# first_line = prediction.split("\n")[0]
# print(first_line)
if prediction.startswith(input_text):
    print(prediction[len(input_text):])


model.save_pretrained("stablecode")
tokenizer.save_pretrained("stablecode")
