import string

import cv2
import nltk
import pytesseract
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from nltk.tokenize import MWETokenizer

nltk.download('gutenberg')

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


class EcSee(BoxLayout):
    def selected(self, filename):
        self.ids.my_image.source = filename[0]
        self.selected_filename = filename[0]
        self.detect_text()

    def detect_text(self):
        # Load the image and perform image processing
        self.image = cv2.imread(self.selected_filename)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.denoised = cv2.fastNlMeansDenoising(self.gray, None, 10, 7, 21)
        self.ret, self.thresh = cv2.threshold(
            self.denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        with open("recognized.txt", "w+") as file:
            file.write("")

        boxes = pytesseract.image_to_data(self.thresh)
        print(boxes)
        for x, b in enumerate(boxes.splitlines()):
            if x != 0:
                b = b.split()
                print(b)
                if len(b) == 12:
                    x, y, w, h = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                    # cv2.rectangle(img(x, y), (w + x, h + y), (0, 0, 255), 3)
                    # cv2.putText(thresh, b[11], (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    file = open("recognized.txt", "a")
                    # text = pytesseract.image_to_string(thresh)

                    text = b[11]
                    text = text.translate(str.maketrans("", "", string.punctuation)).lower()

                    # Appending the text into file
                    file.write(text)
                    file.write(" ")

        file.close()

    def get_tokens(self):
        f = open('recognized.txt')
        raw = f.read()
        tokens = nltk.word_tokenize(raw)
        mwe_tokenizer = MWETokenizer([('kacang', 'tanah'), ('ekstrak', 'malt')])
        tokens = mwe_tokenizer.tokenize(tokens)
        return tokens

    def search_words(self, allergens, tokens):
        occurrences = {}
        for word in allergens:
            if word in tokens:
                occurrences[word] = [i for i, t in enumerate(tokens) if t == word]

        if not occurrences:
            result_text = "Safe"
        else:
            result_text = "Unsafe: " + ', '.join(occurrences.keys())

        self.ids.result_label.text = result_text

        return occurrences


class EcSeeApp(App):

    def build(self):
        return EcSee()

    def detect_allergens(self, instance):
        root = self.root
        root.detect_text()
        tokens = root.get_tokens()
        allergens = [
            "susu",
            "gluten",
            "kedelai",
            "terigu",
            "telur",
            "tomat",
            "kacang",
            "kacang_tanah",
            "kacangkacangan",
            "kacangan",
            "kecap",
            "kayu_manis",
            "ekstrak_malt",
            "sitrus",
            "keju",
            "yoghurt",
            "gandum",
            "vanilla",
            "vanila",
            "cengkeh",
            "krim",
            "mentega",
            "kasein",
            "dadih",
            "custard",
            "diacetyl",
            "ghee",
            "laktalbumin",
            "laktoferin",
            "laktosa",
            "laktulosa",
            "whey",
            "terong",
            "paprika",
            "kentang",
            "terigu",
        ]
        root.search_words(allergens, tokens)


if __name__ == '__main__':
    EcSeeApp().run()
