import os
import codecs
import io

with io.open(os.path.join(os.getcwd() + "/startup/dialogues.txt"), newline='', encoding="utf-8", errors='') as f:
    content = f.read()
    
    for replicas in [dialogue_line.split('\n') for dialogue_line in content.split('\n\n')]:
        if len(replicas) < 2:
            continue
        
        question, answer = replicas[:2]
        question = question[2:]
        answer = answer[2:]

        print(question, answer)