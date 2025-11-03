Libraries needed:

- imagehash - For perceptual hashing
- Pillow (PIL) - Image processing
- boto3 - S3 uploads

  Comparison example:
  import imagehash

  hash1 = imagehash.phash(Image.open(io.BytesIO(screenshot1)))
  hash2 = imagehash.phash(Image.open(io.BytesIO(screenshot2)))

  difference = hash1 - hash2 # Hamming distance (0 = identical)

  if difference > 5: # threshold: 5 bits different # Significant visual change detected
