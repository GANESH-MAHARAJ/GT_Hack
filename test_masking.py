from backend.privacy.masking import mask_pii, safe_unmask, mask_dict

text = "Hi, I'm Ganesh, my number is +91-98765-43210 and email is ganesh@example.com. Order ORD12345 is delayed."
masked, mp = mask_pii(text)

print("MASKED:", masked)
print("MAP:", mp)

# Unmask everything (not what we'll do in production, but for testing)
print("UNMASKED:", safe_unmask(masked, mp))

# Example for dict masking
payload = {
    "message": "Hi, call me at +91-99999-11111",
    "user": {"email": "user@test.com"}
}
masked_obj, mp2 = mask_dict(payload)
print(masked_obj)
print(mp2)
