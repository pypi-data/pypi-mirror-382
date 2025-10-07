from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, BitsAndBytesConfig

# bnb_config = BitsAndBytesConfig(load_in_8bit=True)
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")

article = "UN Chief says there is no military solution in Syria"
inputs = tokenizer(article, return_tensors="pt").to(model.device)
translated_tokens = model.generate(
    **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids("fra_Latn"), max_length=30,
)
result = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

print(result)