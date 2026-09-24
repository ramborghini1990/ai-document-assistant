import io
from PIL import Image, ImageDraw
from app.rag.loader import extract_text_from_image


def test_synthetic_image_transcription():
    print("Testing Vision Transcription on synthetic image with Gemini Tier 1...")

    # ساخت یک عکس تستی حاوی مشخصات خودرو و مصرف سوخت
    img = Image.new("RGB", (800, 300), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    test_content = (
        "AUTORIZZAZIONE TRASPORTO RIFIUTI\n"
        "Targa Mezzo: GF 619 XA\n"
        "Data Revisione: 30/09/2026\n"
        "Consumo Stimato: 14.2 L/100km\n"
        "Stato: REGOLARE"
    )
    d.text((30, 50), test_content, fill=(0, 0, 0))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # اجرای استخراج با موتور چندوجهی
    result = extract_text_from_image(img_bytes, "test_synthetic.png")
    assert len(result) >= 1
    extracted_text = result[0]["text"]
    print("\n--- TRANSCRIBED TEXT FROM IMAGE ---")
    print(extracted_text)
    print("-----------------------------------")

    # بررسی صحت استخراج کلمات کلیدی درون عکس
    assert "GF 619 XA" in extracted_text or "GF619XA" in extracted_text
    assert "30/09/2026" in extracted_text or "2026" in extracted_text
    print("\n✓ Image Vision transcription successfully verified with Tier 1!")


if __name__ == "__main__":
    test_synthetic_image_transcription()
    print("🎉 MULTIMODAL TEST PASSED!")