from IPython.display import display, Markdown, clear_output
import numpy as np
import glob
import random


class Card:
    def __init__(self, question, answer, source=None):
        self.question = question
        self.answer = answer
        self.source = source

    @staticmethod
    def from_lines(q_lines, a_lines, source=None):
        # remove the trimming lines
        for i in reversed(range(len(q_lines))):
            if q_lines[i].strip() == '':
                q_lines.pop(i)
            else:
                break
        for i in reversed(range(len(a_lines))):
            if a_lines[i].strip() == '':
                a_lines.pop(i)
            else:
                break
        return Card(''.join(q_lines), ''.join(a_lines), source)


def read_cards_from_file(path, cards=None):
    state = None
    q = []
    a = []
    if cards is None:
        cards = []
    with open(path, 'r') as f:
        for line in f.readlines():
            token = line.strip()
            if state is None:
                if token == 'Q:':
                    state = 'q'
                elif token == 'A:':
                    raise Exception('Cannot have answer without the question.')
            elif state == 'q':
                if token == 'A:':
                    state = 'a'
                else:
                    q.append(line)
            elif state == 'a':
                if token == '---' or token == 'Q:':
                    cards.append(Card.from_lines(q, a, path))
                    q = []
                    a = []
                    if token == '---':
                        state = None
                    else:
                        state = 'q'
                else:
                    a.append(line)
        if len(q) > 0 or len(a) > 0:
            cards.append(Card.from_lines(q, a, path))
    return cards


def read_cards_from_directory(path, cards=None):
    if cards is None:
        cards = []
    for filename in glob.glob("{}/*.md".format(path)):
        read_cards_from_file(filename, cards)
    return cards


def write_cards(cards, prefix, path=None):
    for i, card in enumerate(cards):
        filename = "{}_{}.md".format(prefix, i + 1)
        if path is not None:
            filename = "{}/{}".format(path, filename)
        print(filename)
        with open(filename, 'w') as f:
            f.write('Q:  \n')
            f.write(card.question)
            f.write('\n')
            f.write('A:  \n')
            f.write(card.answer)


def split_deck(deck_filename, card_prefix, path=None):
    cards = read_cards_from_file(deck_filename)
    write_cards(cards, prefix=card_prefix, path=path)


def learn(cards, 
          randomize=False, 
          show_labels=False,
          show_counter=True,
          max_questions=-1,
          review_failed_ones=False,
          print_failed_card_source=False,
          cls_after_question=False, 
          cls_after_answer=True):
    if review_failed_ones or print_failed_card_source:
        print("---------------------------------------------------------------")
        print("Type anything in the textbox and return to indicate you need to review the card more.")
        print("---------------------------------------------------------------")
    if randomize:
        indices = np.random.permutation(len(cards))
    else:
        indices = range(len(cards))
    if max_questions > 0:
        indices = indices[:max_questions]
    while True:
        more_reviews = []
        counter = 1
        size = len(indices)
        for i in indices:
            card = cards[i]
            if show_labels:
                if show_counter:
                    print("Question ({}/{}):".format(counter, size))
                else:
                    print("Question:")
            display(Markdown(card.question))
            need_review = False
            if input() != '':
                need_review = True

            if cls_after_question:
                clear_output()
            if show_labels:
                print("Answer:")
            display(Markdown(card.answer))
            if input() != '':
                need_review = True
            if cls_after_answer:
                clear_output()
            counter += 1
            if need_review:
                more_reviews.append(i)
        if len(more_reviews) == 0:
            break
        else:
            if review_failed_ones:
                if randomize:
                    random.shuffle(more_reviews)
                indices = more_reviews
            elif print_failed_card_source:
                print("---------------------------------")
                print("Cards that need more review:")
                print("---------------------------------")
                for i in more_reviews:
                    print(cards[i].source)
                break
            else:
                break


