from langchain.llms import HuggingFaceTextGenInference

import warnings
warnings.simplefilter('ignore')

URI = "http://127.0.0.1:8080/"

llm = HuggingFaceTextGenInference(inference_server_url = URI)

print(llm("What is the capital of France?").strip())