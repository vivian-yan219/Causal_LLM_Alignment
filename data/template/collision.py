def collision(graph, story, filter_invalid=False):
    results = []
    N = len(graph.nodes)
    all_cases = story["all_cases"]

    # Does A directly affect B?
    for i in range(N):
        for j in range(N):
            if i == j: continue
            X = graph.nodes[i]
            Y = graph.nodes[j]
            Xn = story["semantic"][X]
            Yn = story["semantic"][Y]
            if not Xn or not Yn: continue
            ans = 'yes' if X in graph.graph[Y]["parent"] else 'no'
            results.append({
                "question": "Does {} directly affect {}?".format(Xn, Yn),
                "answer": ans
            })

    # Is A solely determined by B?
    for i in range(N):
        for j in range(N):
            if i == j: continue
            X = graph.nodes[i]
            Y = graph.nodes[j]
            Xn = story["semantic"][X]
            Yn = story["semantic"][Y]
            if not Xn or not Yn: continue
            if Y not in graph.graph[X]["parent"]:
                ans = 'invalid'
            elif len(graph.graph[X]["parent"]) > 1:
                ans = 'no'
            else:
                ans = 'yes'
            if ans == 'invalid' and filter_invalid: continue
            results.append({
                "question": "Is {} solely determined by {}?".format(Xn, Yn),
                "answer": ans
            })

    # Is A a cause of B?
    for i in range(N):
        for j in range(N):
            if i == j: continue
            X = graph.nodes[i]
            Y = graph.nodes[j]
            Xn = story["semantic"][X]
            Yn = story["semantic"][Y]
            if not Xn or not Yn: continue
            ans = 'yes' if graph.isCause(X, Y) else 'no'
            results.append({
                "question": "Is {} a cuase of {}?".format(Xn, Yn),
                "answer": ans
            })

    # Is A an effect of B?
    for i in range(N):
        for j in range(N):
            if i == j: continue
            X = graph.nodes[i]
            Y = graph.nodes[j]
            Xn = story["semantic"][X]
            Yn = story["semantic"][Y]
            if not Xn or not Yn: continue
            ans = 'yes' if graph.isCause(Y, X) else 'no'
            results.append({
                "question": "Is {} an effect of {}?".format(Xn, Yn),
                "answer": ans
            })

    #  if {A=a} and {B=b}, can we infer that {C=c} ? 
    if all_cases:
        for i in range(N-1):
            for j in range(i+1, N):
                for k in range(N):
                    if i == k or j == k:
                        continue
                    for P in [0, 1]:
                        for Q in [0, 1]:
                            for R in [0, 1]:
                                X = graph.nodes[i]
                                Y = graph.nodes[j]
                                Z = graph.nodes[k]
                                Xs = story["semantic"][X + str(P)]
                                Ys = story["semantic"][Y + str(Q)]
                                Zs = story["semantic"][Z + str(R)]
                                if not Xs or not Ys or not Zs: continue

                                ans = 'invalid'
                                for case in all_cases:
                                    if case[X] == P and case[Y] == Q:
                                        if case[Z] != R:
                                            ans = 'no'
                                        elif ans == 'invalid':
                                            ans = 'yes'
                                if ans == 'invalid' and filter_invalid: continue
                                results.append({
                                    "question": "If {} and {}, can we infer that {}?".format(Xs, Ys, Zs),
                                    "answer": ans
                                })

    #  if {A=a}, can we infer that {B=b} ?
    if all_cases:
        for i in range(N):
            for j in range(N):
                if i == j: continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        X = graph.nodes[i]
                        Y = graph.nodes[j]
                        Xs = story["semantic"][X + str(P)]
                        Ys = story["semantic"][Y + str(Q)]
                        if not Xs or not Ys: continue

                        ans = 'yes'
                        for case in all_cases:
                            if case[X] == P and case[Y] != Q:
                                ans = 'no'
                                break
                        
                        results.append({
                            "question": "If {}, can we infer that {}?".format(Xs, Ys),
                            "answer": ans
                        })

    #  Is {A=a} sufficient to cause {B=b} ?
    if all_cases:
        for i in range(N):
            for j in range(N):
                if i == j: continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        X = graph.nodes[i]
                        Y = graph.nodes[j]
                        Xn = story["semantic"][X + str(P) + '_noun']
                        Yn = story["semantic"][Y + str(Q) + '_noun']
                        if not Xn or not Yn: continue
                        if not graph.isCause(X, Y):  # X should be Y's cause
                            ans = 'invalid'
                        else:
                            ans = 'yes'
                            for case in all_cases:
                                if case[X] == P and case[Y] != Q:
                                    ans = 'no'
                                    break
                        if ans == 'invalid' and filter_invalid: continue
                        results.append({
                            "question": "Is {} sufficient to cause {}?".format(Xn, Yn),
                            "answer": ans
                        })

    #  Is {A=a} necessary to cause {B=b} ?
    if all_cases:
        for i in range(N):
            for j in range(N):
                if i == j: continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        X = graph.nodes[i]
                        Y = graph.nodes[j]
                        Xn = story["semantic"][X + str(P) + '_noun']
                        Yn = story["semantic"][Y + str(Q) + '_noun']
                        if not Xn or not Yn: continue
                        if not graph.isCause(X, Y):  # X should be Y's cause
                            ans = 'invalid'
                        else:
                            ans = 'yes'
                            for case in all_cases:
                                if case[Y] == Q and case[X] != P:
                                    ans = 'no'
                                    break
                        if ans == 'invalid' and filter_invalid: continue
                        results.append({
                            "question": "Is {} necessary to cause {}?".format(Xn, Yn),
                            "answer": ans
                        })

    # Does {A=a} always result in {B=b} ?
    if all_cases:
        for i in range(N):
            for j in range(N):
                if i == j: continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        X = graph.nodes[i]
                        Y = graph.nodes[j]
                        Xn = story["semantic"][X + str(P) + '_noun']
                        Yn = story["semantic"][Y + str(Q) + '_noun']
                        if not Xn or not Yn: continue
                        if not graph.isCause(X, Y):
                            ans = 'no'
                        else:
                            ans = 'yes'
                            for case in all_cases:
                                if case[X] == P and case[Y] != Q:
                                    ans = 'no'
                                    break
                        results.append({
                            "question": "Does {} always result in {}?".format(Xn, Yn),
                            "answer": ans
                        })

    # Does {A=a} directly cause {B=b}?
    if all_cases:
        for i in range(N):
            for j in range(N):
                if i == j: continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        X = graph.nodes[i]
                        Y = graph.nodes[j]
                        Xn = story["semantic"][X + str(P) + '_noun']
                        Yn = story["semantic"][Y + str(Q) + '_noun']
                        if not Xn or not Yn: continue
                        if X not in graph.graph[Y]["parent"]:
                            ans = 'no'
                        else:
                            ans = 'yes'
                            for case in all_cases:
                                if case[X] == P and case[Y] != Q:
                                    ans = 'no'
                                    break
                        results.append({
                            "question": "Does {} directly cause {}?".format(Xn, Yn),
                            "answer": ans
                        })

    # (counterfactual) if {A=a}, would still {B=b}?
    if all_cases:
        for X in graph.nodes:
            for Y in graph.nodes:
                if not graph.isCause(X, Y): continue
                for P in [0, 1]:
                    for Q in [0, 1]:
                        flag = False
                        for case in all_cases:
                            if case[X] == 1 - P and case[Y] == Q:
                                flag = True
                                break

                        if not flag: continue
                        Xn = story["semantic"][X + str(P) + '_past']
                        Yn = story["semantic"][Y + str(Q) + '_present']
                        if not Xn or not Yn: continue
                        right, wrong = False, False
                        for case in all_cases:
                            if case[X] == P:
                                if case[Y] == Q:
                                    right = True
                                else:
                                    wrong = True
                        if right and not wrong:
                            ans = 'yes'
                        elif not right and wrong:
                            ans = 'no'
                        elif right and wrong:
                            ans = 'not sure'
                        else:
                            ans = 'invalid'
                        if ans == 'invalid' and filter_invalid: continue
                        results.append({
                            "question": "If {}, would {}?".format(Xn, Yn),
                            "answer": ans
                        })

    return results
