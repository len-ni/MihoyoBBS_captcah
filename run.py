import onnxruntime as ort
import numpy as np


def geetest39_1(image1, image2, model_path):
    image1 = image1.convert("RGB")
    image2 = image2.convert("RGB")
    model = ort.InferenceSession(model_path)
    
    def process_pair_classifier_ans_image(image, input_shape=(32, 32)):
        sub_image = image.resize(input_shape)
        return np.array(sub_image).transpose(2, 0, 1)[np.newaxis, ...] / 255.0
    
    def run_prediction(output_names, input_feed):
            return model.run(output_names, input_feed)

    left = process_pair_classifier_ans_image(image1)
    right = process_pair_classifier_ans_image(image2)
    prediction = run_prediction(None, {'input_left': left.astype(np.float32),
                                    'input_right': right.astype(np.float32)})[0]
    prediction_value = prediction[0][0]
    formatted_value = "{:.5f}".format(prediction_value)
    return float(formatted_value)
