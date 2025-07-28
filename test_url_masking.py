import sys
sys.path.append('src')

from config import mask_sensitive_url

# Test IFTTT URL masking
test_url = "https://maker.ifttt.com/trigger/nintendo_museum_slot_available/with/key/lqzUGg0QQ-P4erVcnepAKNjKY7W_jqzJb0WkNR5Ebte"
masked_url = mask_sensitive_url(test_url)

print("Original URL:")
print(test_url)
print("\nMasked URL:")
print(masked_url)

# Test other URL types
test_urls = [
    "https://api.example.com/webhook?key=secret123",
    "https://example.com/api?token=abc123&other=value",
    "https://normal-url.com/path",
    "https://maker.ifttt.com/trigger/event/with/key/supersecretkey123"
]

print("\nOther URL tests:")
for url in test_urls:
    print(f"Original: {url}")
    print(f"Masked:   {mask_sensitive_url(url)}")
    print()
