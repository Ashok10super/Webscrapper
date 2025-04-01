from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": " Hsr Layout is in which hobli and which direction and which city in bengaluru give the answer in this format city,direction,hobli search hobli deeply and give answers"}
  ]
)

print(completion.choices[0].message);
