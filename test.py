cards = ["Machine Learning", "AI", "Cyber Security", "Deep Learning"]

selected_card = ["Cyber Security"]

for i,card in enumerate(cards):
    if card in selected_card:
        selected_card.remove(card)

print(selected_card)