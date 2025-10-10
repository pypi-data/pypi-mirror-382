

def predict_accuracy(real, predict):
    if len(real) != len(predict):
        raise ValueError(f"样本真实值与预测值列表长度需相同")
    cnt = 0
    for i in range(len(real)):
        if real[i] == predict[i]:
            cnt += 1
    return cnt / len(real)


def confusion_matrix(real, predict, sort=False):
    class_index = []

    for i in range(len(real)):
        if not real[i] in class_index:
            class_index.append(real[i])
    if sort == True:
        class_index.sort()
    con_matrix = [[0 for i in range(len(class_index))] for j in range(len(class_index))]
    for i in range(len(predict)):
        for j in range(len(class_index)):
            if real[i] == class_index[j]:
                for k in range(len(class_index)):
                    if predict[i] == class_index[k]:
                        con_matrix[j][k] += 1
                        break
                break

    return con_matrix, class_index







