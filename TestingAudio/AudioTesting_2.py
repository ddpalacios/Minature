# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai

openai.api_key = "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"
# response = openai.ChatCompletion.create(
#   model="gpt-3.5-turbo",
#   messages=[
#         {"role": "system", "content": "You are a helpful assistant."}
#     ]
# )
#
# print(response['choices'][0]['message'].content)

idx = 0
while idx < 10:
    message =input("User > ")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": message}
        ]
    )

    print(response['choices'][0]['message'].content)
    idx+=1
    print("{} message complete.".format(idx))


