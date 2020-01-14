class Card:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    @staticmethod
    def from_lines(q_lines, a_lines):
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
        return Card(''.join(q_lines), ''.join(a_lines))



def read_cards(path):
    state = None
    q = []
    a = []
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
                    cards.append(Card.from_lines(q, a))
                    q = []
                    a = []
                    if token == '---':
                        state = None
                    else:
                        state = 'q'
                else:
                    a.append(line)
        if len(q) > 0 or len(a) > 0:
            cards.append(Card.from_lines(q, a))
    return cards


if __name__ == '__main__':
    cards = read_cards('./cards/sample.md')
    print(len(cards))
    # print("------------------")
    # print(cards[1].question)
    # print("------------------")
    # print(cards[1].answer)
    # print("------------------")