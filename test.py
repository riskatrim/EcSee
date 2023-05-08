import string

import cv2
import nltk
import pytesseract
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

nltk.download('gutenberg')

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


class Test(BoxLayout):
    def __init__(self, **kwargs):
        super(Test, self).__init__(**kwargs)
        self.allergen_count = 0

    def selected(self, filename):
        self.ids.my_image.source = filename[0]
        self.selected_filename = filename[0]
        self.allergen_count = 0  # Reset the allergen count to zero
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

    def detection_accuracy(self):
        osd = pytesseract.image_to_osd(self.thresh)
        confidence_index = osd.index("Orientation confidence")
        confidence_level = float(osd[confidence_index + len("Orientation confidence") + 2:].split()[0])
        accuracy_percentage = confidence_level * 10
        accuracy_percentage = min(accuracy_percentage, 100)  # limit to 100%
        accuracy_result = f"Detection accuracy: {accuracy_percentage: }%"
        self.ids.accuracy_label.text = accuracy_result

    def count_allergens(self, button):
        self.ids.my_button1 = button
        self.allergen_count += 1
        allergens = [
            "susu",
            "gluten",
            "kedelai",
            "terigu",
            "telur",
            "tomat",
            "kacang",
        ]
        tokens = self.get_tokens()
        self.allergen_accuracy(allergens, tokens)

    def allergen_accuracy(self, allergens, tokens):

        occurrences = self.search_words(allergens, tokens)
        num_detected = len(occurrences)

        num_actual = self.allergen_count

        if num_actual != 0:
            accuracy = (num_detected / num_actual) * 100
        else:
            if num_actual == 0:
                accuracy = 100
            else:
                accuracy = 0

        allergen_accuracy_result = f'Allergen detection accuracy: {accuracy: }%\n'
        self.ids.filtering_label.text = allergen_accuracy_result


class TestApp(App):
    def build(self):
        return Test()

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
        ]
        root.search_words(allergens, tokens)
        root.detection_accuracy()
        root.allergen_accuracy(allergens, tokens)


if __name__ == '__main__':
    TestApp().run()
