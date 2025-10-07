
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from whisperlivekit.translation.translation import load_model, translate

def benchmark_standard(text):
    print("\nStandard Transformers:")
    # Initialize model and tokenizer once
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    
    # Measure only inference time
    start = time.time()
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    translated_tokens = model.generate(
        **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids("fra_Latn"), max_length=30,
    )
    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    inference_time = time.time() - start
    
    print(f"Translation: {translation}")
    print(f"Inference time: {inference_time:.4f}s")
    return inference_time

def benchmark_ctranslate2(text):
    print("\nCTranslate2:")
    # Initialize model once
    translation_model = load_model(["en"])
    
    # Measure only inference time
    start = time.time()
    translation = translate(text, translation_model, "fra_Latn", "en")
    inference_time = time.time() - start
    
    print(f"Translation: {translation}")
    print(f"Inference time: {inference_time:.4f}s")
    return inference_time

def run_benchmarks():
    test_texts = [
        "UN Chief says there is no military solution in Syria",
        "The rapid advancement of AI technology is transforming various industries",
        "Climate change poses a significant threat to global ecosystems",
        "International cooperation is essential for addressing global challenges",
        "The development of renewable energy sources is crucial for a sustainable future"
    ]
    
    total_std_time = 0
    total_ctranslate2_time = 0
    
    for text in test_texts:
        print(f"\nTesting text: {text}")
        std_time = benchmark_standard(text)
        ctranslate2_time = benchmark_ctranslate2(text)
        
        total_std_time += std_time
        total_ctranslate2_time += ctranslate2_time
        
        print(f"\nSpeed comparison for this text:")
        print(f"Standard: {std_time:.4f}s")
        print(f"CTranslate2: {ctranslate2_time:.4f}s")
        print(f"CTranslate2 is {(std_time/ctranslate2_time):.1f}x faster")
        print("-" * 50)
    
    print(f"\nOverall speed comparison:")
    print(f"Total Standard time: {total_std_time:.4f}s")
    print(f"Total CTranslate2 time: {total_ctranslate2_time:.4f}s")
    print(f"CTranslate2 is {(total_std_time/total_ctranslate2_time):.1f}x faster overall")

if __name__ == "__main__":
    run_benchmarks()
