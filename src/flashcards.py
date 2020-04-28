from IPython.display import display, Markdown, clear_output
import numpy as np
import glob
import random
import shutil


class Card:
    def __init__(self, question, answer, src=None):
        self.question = question
        self.answer = answer
        self.src = src

    @staticmethod
    def from_lines(q_lines, a_lines, src=None):
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
        return Card(''.join(q_lines), ''.join(a_lines), src)


def read_cards_from_file(path, cards=None):
    state = None
    q = []
    a = []
    if cards is None:
        cards = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            token = line.strip()
            if state is None:
                if token == "Q:" or token == "﻿Q:":
                    state = 'q'
                elif token == 'A:' or token == "A:":
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
          show_filename=False,
          max_questions=-1,
          review_failed_ones=False,
          print_report_card=False,
          cls_after_question=False,
          cls_after_answer=True):
    if randomize:
        indices = np.random.permutation(len(cards))
    else:
        indices = np.arange(len(cards))
    if max_questions > 0:
        indices = indices[:max_questions]
    original_indices = indices
    original_indices.sort()
    passed_cards = []
    failed_cards = []
    attempt = 1

    if review_failed_ones or print_report_card:
        print("---------------------------------------------------------------")
        print("Type anything in the textbox and return to indicate you need to review the card more.")
        print("---------------------------------------------------------------")
    while True:
        more_reviews = []
        counter = 1
        size = len(indices)
        for i in indices:
            card = cards[i]
            if show_filename:
                print("file: {}".format(card.src))
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
            if attempt == 1:
                if need_review:
                    failed_cards.append(i)
                else:
                    passed_cards.append(i)
        if len(more_reviews) == 0:
            break
        else:
            if review_failed_ones:
                if randomize:
                    random.shuffle(more_reviews)
                indices = more_reviews
            else:
                break
        attempt += 1
    if print_report_card:
        passed_cards.sort()
        failed_cards.sort()
        print("---------------------------------")
        print("Report Card:")
        print("---------------------------------")
        print("PASSED:")
        for i in passed_cards:
            print(" ", cards[i].src)
        print()
        print("FAILED:")
        for i in failed_cards:
            print(" ", cards[i].src)
    return passed_cards, failed_cards


def lietner_learning(root_path, num_boxes, current_box, max_questions, review_failed_ones=True, show_filename=False, verbose=False):
    path = "{}/box{}".format(root_path, current_box)
    cards = read_cards_from_directory(path)
    if len(cards) == 0:
        raise Exception("No cards in {}".format(path))
    passed, failed = learn(cards,
                           randomize=True,
                           show_labels=True,
                           show_counter=True,
                           show_filename=show_filename,
                           max_questions=max_questions,
                           review_failed_ones=review_failed_ones,
                           print_report_card=True,
                           cls_after_question=False,
                           cls_after_answer=True)
    if current_box < num_boxes:
        target_path = "{}/box{}/".format(root_path, current_box+1)
        for i in passed:
            shutil.move(cards[i].src, target_path)
            if verbose:
                print("moved {} to {}".format(cards[i].src, target_path))
    if current_box > 1:
        target_path = "{}/box1/".format(root_path)
        for i in failed:
            shutil.move(cards[i].src, target_path)
            if verbose:
                print("moved {} to {}".format(cards[i].src, target_path))


if __name__ == '__main__':
    lietner_learning('/Users/dgu/Projects/learning/flashcards/test', 3, 3, 2, verbose=True)
