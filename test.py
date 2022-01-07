import os
import codecs

with codecs.open(os.path.join(os.getcwd() + "/startup/dialogues.txt"), "r", "utf_8_sig") as f:
    content = f.read()

    dialogues = [dialogue_line.split('\n') for dialogue_line in content.split('\n\n')]
    
    for replicas in dialogues:
        if len(replicas) < 2:
            continue
        
        question, answer = replicas[:2]
        question = question[2:]
        answer = answer[2:]

        print([question, answer])

