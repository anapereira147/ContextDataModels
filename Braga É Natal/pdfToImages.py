import fitz
import PIL.Image
import io 

pdf = fitz.open("Programa_BragaENatal24.pdf")
counter = 1

for i in range(len(pdf)):
    page = pdf[i]
    images = page.get_images()
    for image in images:
        base_img = pdf.extract_image(image[0])
        image_data = base_img["image"]
        img = PIL.Image.open(io.BytesIO(image_data))
        extension = base_img["ext"]
        img.save(open(f"image{counter}.{extension}", "wb"))
        counter += 1
    



    