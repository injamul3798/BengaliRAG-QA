import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def create_test_pdf():
    # Register Bengali font (using a standard font for now)
    pdf_path = "tests/data/test.pdf"
    c = canvas.Canvas(pdf_path)
    
    # Add Bengali text
    text = """আি আমাি ব্ স সাতাি মাত্র। এ িীব্নটা না দদকঘিযি র্হসাকব্ ব়্ে, না গুকনি র্হসাকব্। তব্ুইহাি একটুর্ব্কিষ
মূলয আকি।ইহা যসই ফু কলি মকতা োহাি ব্ুককি উপকি ভ্রমি আর্স া ব্র্স ার্িল, এব্ং যসই পদকক্ষকপি ইর্তহাস
তাহাি িীব্কনি মাঝখাকনফকলি মকতা গুটি ধর্ি া উঠি াকি।

যসই ইর্তহাসটুকুআকাকি যিাকটা, তাহাকক যিাকটা কর্ি াই জলর্খব্। যিাকটাকক েঁাহািা সামানয ব্জল া ভুল ককিন
না তঁ াহািা ইহাি িস ব্ুজঝকব্ন। ককলকি েতগুকলা পিীক্ষা পাি কর্িব্াি সব্ আর্ম চুকাই ার্ি। যিকলকব্লা
আমাি সুন্দি যচহািা লই া পজণ্ডতমিা আমাকক র্িমুল ফু ল ও মাকাল ফকলি সর্হত তুলনা কর্ি া, র্ব্দ্রুপ কর্িব্াি সুু্কোগ
পাই ার্িকলন।"""
    
    # Write text to PDF
    c.drawString(72, 800, text)
    c.save()

if __name__ == "__main__":
    create_test_pdf()
