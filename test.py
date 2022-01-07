import os

with open(os.path.join(os.getcwd() + "/startup/dialogues.txt")) as f:
    content = f.read()
    for dialogue_line in content.split('\n\n'):
        print(dialogue_line)

    dialogues = [dialogue_line.split('\n') for dialogue_line in content.split('\n\n')]
    
    for replicas in dialogues:
        if len(replicas) < 2:
            continue
        
        question, answer = replicas[:2]
        question = question[2:]
        answer = answer[2:]

        print([question, answer])

