import math


def label_modify_2_classify(label):
    label_type = []
    for i in range(len(label)):
        if not label[i] in label_type:
            label_type.append(label[i])

    if len(label_type) != 2:
        raise ValueError(f"输入的标签列表需只有两种标签")
    elif 0 in label_type and 1 in label_type:
        return label
    elif 1 in label:
        for i in range(len(label)):
            if label[i] != 1:
                label[i] = 0
        return label
    elif 0 in label:
        for i in range(len(label)):
            if label[i] != 0:
                label[i] = 1
        return label
    else:
        for i in range(len(label)):
            if label[i] == label_type[0]:
                label[i] = 0
            elif label[i] == label_type[1]:
                label[i] = 1
        return label


def Min_Max_Scaling(feature):
    feature_scaled = [[] for i in range(len(feature))]
    for i in range(len(feature[0])):
        max = -math.inf
        min = math.inf
        for j in range(len(feature)):
            if feature[j][i] > max:
                max = feature[j][i]
            elif feature[j][i] < min:
                min = feature[j][i]

        for j in range(len(feature)):
            feature_scaled[j].append((feature[j][i] - min) / (max - min))

    return feature_scaled


def Standardization(feature):
    feature_scaled = [[] for i in range(len(feature))]
    for i in range(len(feature[0])):
        sum = 0
        for j in range(len(feature)):
            sum += feature[j][i]
        avg = sum / len(feature)

        sum = 0
        for j in range(len(feature)):
            sum += (feature[j][i] - avg) ** 2
        dev = math.sqrt(sum / len(feature))

        for j in range(len(feature)):
            feature_scaled[j].append((feature[j][i] - avg) / dev)

    return feature_scaled


def one_hot_encode(label):
    class_num = max(label) + 1
    one_hot_dict = {}
    for i in range(class_num):
        one_hot_list = [0 for _ in range(class_num)]
        one_hot_list[i] = 1
        one_hot_dict[i] = one_hot_list

    label_one_hot = []
    for i in range(len(label)):
        label_one_hot.append(one_hot_dict[label[i]])

    return label_one_hot

def one_hot_decode(label_one_hot):
    class_num = len(label_one_hot[0])
    restore_one_hot_dict = {}
    for i in range(class_num):
        one_hot_list = [0 for _ in range(class_num)]
        one_hot_list[i] = 1
        restore_one_hot_dict[tuple(one_hot_list)] = i

    label = []
    for i in range(len(label_one_hot)):
        label.append(restore_one_hot_dict[tuple(label_one_hot[i])])
    return label

def flatten(x):
    x_flattened = []
    for i in range(len(x)):
        sample = []
        for j in range(len(x[i])):
            for k in range(len(x[i][j])):
                sample.append(x[i][j][k])
        x_flattened.append(sample)
    return x_flattened


