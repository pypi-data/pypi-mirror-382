import math
import copy
import random
import warnings
from tqdm import tqdm
import numpy as np
from draft_basic import activation_function
from draft_basic import basic_function

class MLP:
    def __init__(self, input_node_num, hidden_node_num, hidden_activation='relu', target='2_classify', output_node_num=1):
        self.input_node_num = input_node_num
        self.hidden_node_num = hidden_node_num
        self.output_node_num = output_node_num
        if input_node_num < 1 or input_node_num != int(input_node_num):
            raise ValueError(f"输入层节点数量非法")
        if hidden_node_num < 1 or hidden_node_num != int(hidden_node_num):
            raise ValueError(f"隐藏层节点数量非法")
        if output_node_num < 1 or output_node_num != int(output_node_num):
            raise ValueError(f"输出层节点数量非法")

        hidden_weight = []
        for i in range(hidden_node_num):
            weight_list = []
            for j in range(input_node_num + 1):
                weight_list.append(random.random())
            hidden_weight.append(weight_list)
        self.hidden_weight = hidden_weight
        if target == '2_classify' or target == 'output_1_node_regress':
            output_weight = []
            for i in range(hidden_node_num + 1):
                output_weight.append(random.random())
            self.output_weight = output_weight
        elif target == 'multi_classify' or target == 'output_multi_node_regress':
            output_weight = []

            for i in range(output_node_num):
                weight_list = []
                for j in range(hidden_node_num + 1):
                    weight_list.append(random.random())
                output_weight.append(weight_list)
            self.output_weight = output_weight
        else:
            raise ValueError(f"target可选2_classify、output_1_node_regress、multi_classify及output_multi_node_regress四者之一\n（‘注：output_1_node_regress只支持输出层单节点回归（标签形如[1,2,1,...]），output_multi_node_regress可支持输出层多节点回归（标签形如[[1,2],[2,1],...]）’）")

        self.hidden_activation = hidden_activation
        self.target = target


        self.loss_values = []
        self.valid_loss_values = []
        self.accuracy_list = []
        self.valid_accuracy_list = []

        self.min_valid_loss = math.inf
        self.min_valid_cnt = 0
        self.validation_set_early_stop = False
        self.hidden_weight_early_stop_memory = copy.deepcopy(self.hidden_weight)
        self.output_weight_early_stop_memory = copy.deepcopy(self.output_weight)
        self.early_stop_memory = False



    def train(self, x_train, y_train, x_valid='NULL', y_valid='NULL', lr=0.01, epochs=100, batch_size=1, verbose_frequency=1, methods=False):
        if len(x_train) % batch_size != 0:
            raise ValueError(f"batch_size需为训练集样本数量的约数")

        if isinstance(methods, dict):
            for method in methods:
                if not (method == 'lr_decay' or method == 'validation_set_early_stop'):
                    raise ValueError(f"目前methods支持lr_decay及validation_set_early_stop")
                if method == 'lr_decay':
                    """
                    if not methods['lr_decay'][0] == 'exp_decay' \
                            and not methods['lr_decay'][0] == 'decay_based_on_validation_set':
                        raise ValueError(f"目前lr_decay支持exp_decay与decay_based_on_validation_set")
                    """

                    if not isinstance(methods['lr_decay'], list):
                        raise ValueError(f"lr_decay的值应为一个2维列表，形如['exp_decay', 0.01]")
                    if len(methods['lr_decay']) != 2:
                        raise ValueError(f"lr_decay的值应为一个2维列表，形如['exp_decay', 0.01]")
                    if not methods['lr_decay'][0] == 'exp_decay':
                        raise ValueError(f"目前lr_decay支持exp_decay")
                    else:
                        if methods['lr_decay'][0] == 'exp_decay':
                            if not isinstance(methods['lr_decay'][1], (int, float)):
                                raise ValueError(f"列表第二列请输入正确的整形或字符型衰减率")
                        """
                        if methods['lr_decay'][0] == 'decay_based_on_validation_set':
                            if not isinstance(methods['lr_decay'][1], int) \
                                    or not isinstance(methods['lr_decay'][2], float):
                                raise ValueError(f"列表第二列请输入正确的整形代数，第三列请输入正确的浮点型学习率衰减倍数")
                            if methods['lr_decay'][2] <= 0 or methods['lr_decay'][2] >= 1:
                                warnings.warn("衰减倍数可能不合法", UserWarning)
                        """

                    lr0 = lr
                if method == 'validation_set_early_stop':
                    if not isinstance(methods['validation_set_early_stop'], list):
                        raise ValueError(f"validation_set_early_stop的值应为一个2维列表，形如[50, True]")
                    if len(methods['validation_set_early_stop']) != 2:
                        raise ValueError(f"validation_set_early_stop的值应为一个2维列表，形如[50, True]")
                    if not isinstance(methods['validation_set_early_stop'][0], int):
                        raise ValueError(f"请输入合法的验证集提前终止代数（整形）")
                    else:
                        if not isinstance(methods['validation_set_early_stop'][1], bool):
                            raise ValueError(f"validation_set_early_stop的值列表第二位请输入True或False以确定是否保存最优参数")
                        else:
                            self.validation_set_early_stop = methods['validation_set_early_stop'][0]
                            self.early_stop_memory = methods['validation_set_early_stop'][1]

        ac = getattr(activation_function, self.hidden_activation)
        ac_derivative = getattr(activation_function, self.hidden_activation + '_derivative')
        if self.target == '2_classify':
            for _ in tqdm(range(epochs)):
                text = f'第{_ + 1}代'
                if isinstance(methods, dict):
                    if 'lr_decay' in methods:
                        lr = lr0 * np.exp(-methods['lr_decay'][1] * _)
                        text += f'学习率：{lr}，'


                indices = list(range(len(x_train)))
                random.shuffle(indices)

                # 使用打乱的索引重新排序两个列表
                x_random_train = [x_train[index] for index in indices]
                y_random_train = [y_train[index] for index in indices]

                x_batch_list = []
                y_batch_list = []
                for i in range(len(x_random_train) // batch_size):
                    x_batch_list.append(x_random_train[batch_size * i:batch_size * (i + 1)])
                    y_batch_list.append(y_random_train[batch_size * i:batch_size * (i + 1)])

                epoch_loss = 0
                cnt = 0

                for batch in range(len(x_random_train) // batch_size):

                    hidden_gradient = []
                    output_gradient = []

                    for i in range(len(x_batch_list[batch])):

                        x_sample = [x_batch_list[batch][i][index] for index in range(len(x_batch_list[batch][i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = 0
                        for j in range(self.hidden_node_num + 1):
                            output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

                        predict = activation_function.sigmoid(output_layer_output)

                        pred_result = 1 if predict >= 0.5 else 0

                        if pred_result == y_batch_list[batch][i]:
                            cnt += 1

                        # 交叉熵损失
                        epsilon = 1e-10
                        cross_entropy_loss = - (y_batch_list[batch][i] * np.log(predict + epsilon) + (
                                    1 - y_batch_list[batch][i]) * np.log(1 - predict + epsilon))

                        epoch_loss += cross_entropy_loss  # 累加损失

                        sample_gradient = []
                        for j in range(self.hidden_node_num):
                            gradient = []
                            for k in range(self.input_node_num + 1):
                                gradient.append((predict - y_batch_list[batch][i]) * self.output_weight[j] * ac_derivative(
                                    hidden_layer_output[j]) * x_sample[k])
                            sample_gradient.append(gradient)
                        hidden_gradient.append(sample_gradient)
                        sample_gradient = []
                        for j in range(self.hidden_node_num + 1):
                            sample_gradient.append((predict - y_batch_list[batch][i]) * hidden_layer_ac_output[j])
                        output_gradient.append(sample_gradient)

                    hidden_gradient_sum = [[0 for num in range(self.input_node_num + 1)] for _ in range(self.hidden_node_num)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_gradient_sum[j][k] += hidden_gradient[item][j][k]

                    output_gradient_sum = [0 for num in range(self.hidden_node_num + 1)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num + 1):
                            output_gradient_sum[j] += output_gradient[item][j]

                    for j in range(self.hidden_node_num):
                        for k in range(self.input_node_num + 1):
                            self.hidden_weight[j][k] -= lr * hidden_gradient_sum[j][k] / len(x_batch_list)

                    for j in range(self.hidden_node_num + 1):
                        self.output_weight[j] -= lr * output_gradient_sum[j] / len(x_batch_list)
                self.loss_values.append(epoch_loss / len(x_train))
                self.accuracy_list.append(cnt / len(x_train))
                if isinstance(x_valid, list) and isinstance(y_valid, list):
                    valid_epoch_loss = 0
                    valid_cnt = 0
                    for i in range(len(x_valid)):
                        x_sample = [x_valid[i][index] for index in range(len(x_valid[i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = 0
                        for j in range(self.hidden_node_num + 1):
                            output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

                        predict = activation_function.sigmoid(output_layer_output)

                        pred_result = 1 if predict >= 0.5 else 0
                        if pred_result == y_valid[i]:
                            valid_cnt += 1
                        epsilon = 1e-10
                        cross_entropy_loss = - (y_valid[i] * np.log(predict + epsilon) + (
                                1 - y_valid[i]) * np.log(1 - predict + epsilon))

                        valid_epoch_loss += cross_entropy_loss  # 累加损失
                    self.valid_loss_values.append(valid_epoch_loss / len(x_valid))
                    self.valid_accuracy_list.append(valid_cnt / len(x_valid))
                if (_ + 1) % verbose_frequency == 0:
                    text += f'损失：{self.loss_values[-1]}，准确率：{self.accuracy_list[-1] * 100}%'
                    if isinstance(x_valid, list) and isinstance(y_valid, list):
                        text += f"，验证集损失：{self.valid_loss_values[-1]}，验证集准确率：{self.valid_accuracy_list[-1] * 100}%"
                    print(text)

                if isinstance(x_valid, list) and isinstance(y_valid, list) and self.validation_set_early_stop is not False:
                    if self.valid_loss_values[-1] < self.min_valid_loss:
                        self.min_valid_cnt = 0
                        self.min_valid_loss = self.valid_loss_values[-1]
                        if self.early_stop_memory is True:
                            self.hidden_weight_early_stop_memory = copy.deepcopy(self.hidden_weight)
                            self.output_weight_early_stop_memory = copy.deepcopy(self.output_weight)
                    else:
                        self.min_valid_cnt += 1

                if self.min_valid_cnt == self.validation_set_early_stop and self.validation_set_early_stop is not False:
                    if self.early_stop_memory is True:
                        self.hidden_weight = copy.deepcopy(self.hidden_weight_early_stop_memory)
                        self.output_weight = copy.deepcopy(self.output_weight_early_stop_memory)
                    print(f'验证集损失{self.validation_set_early_stop}代不减小，提前终止')
                    break


            if isinstance(x_valid, list) and isinstance(y_valid, list):
                return self.loss_values, self.accuracy_list, self.valid_loss_values, self.valid_accuracy_list
            else:
                return self.loss_values, self.accuracy_list

        if self.target == 'multi_classify':
            for _ in tqdm(range(epochs)):
                text = f'第{_ + 1}代'
                if isinstance(methods, dict):
                    if 'lr_decay' in methods:
                        lr = lr0 * np.exp(-methods['lr_decay'][1] * _)
                        text += f'学习率：{lr}，'

                indices = list(range(len(x_train)))
                random.shuffle(indices)

                # 使用打乱的索引重新排序两个列表
                x_random_train = [x_train[index] for index in indices]
                y_random_train = [y_train[index] for index in indices]

                x_batch_list = []
                y_batch_list = []
                for i in range(len(x_random_train) // batch_size):
                    x_batch_list.append(x_random_train[batch_size * i:batch_size * (i + 1)])
                    y_batch_list.append(y_random_train[batch_size * i:batch_size * (i + 1)])

                epoch_loss = 0
                cnt = 0


                for batch in range(len(x_random_train) // batch_size):

                    hidden_gradient = []
                    output_gradient = []

                    for i in range(len(x_batch_list[batch])):

                        x_sample = [x_batch_list[batch][i][index] for index in range(len(x_batch_list[batch][i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = [0 for num in range(self.output_node_num)]
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]

                        predict_list = []
                        for j in range(self.output_node_num):
                            predict = activation_function.softmax(j, output_layer_output)
                            predict_list.append(predict)

                        pred_result = [0 for num in range(self.output_node_num)]
                        max_prob = max(predict_list)
                        index = predict_list.index(max_prob)
                        pred_result[index] = 1

                        if pred_result == y_batch_list[batch][i]:
                            cnt += 1


                        # 交叉熵损失
                        epsilon = 1e-10
                        categorical_cross_entropy_loss = 0
                        for j in range(self.output_node_num):
                            categorical_cross_entropy_loss += -y_batch_list[batch][i][j] * np.log(predict_list[j])
                        epoch_loss += categorical_cross_entropy_loss  # 累加损失

                        sample_gradient = []
                        for j in range(self.hidden_node_num):
                            gradient = []
                            for k in range(self.input_node_num + 1):
                                sigma = 0
                                for p in range(self.output_node_num):
                                    sigma += self.output_weight[p][j] * (predict_list[p] - y_batch_list[batch][i][p])

                                gradient.append(sigma * ac_derivative(hidden_layer_output[j]) * x_sample[k])
                            sample_gradient.append(gradient)
                        hidden_gradient.append(sample_gradient)
                        sample_gradient = []
                        for j in range(self.output_node_num):
                            gradient = []
                            for k in range(self.hidden_node_num + 1):
                                gradient.append(
                                    (predict_list[j] - y_batch_list[batch][i][j]) * hidden_layer_ac_output[k])
                            sample_gradient.append(gradient)
                        output_gradient.append(sample_gradient)

                    hidden_gradient_sum = [[0 for __ in range(self.input_node_num + 1)] for _ in range(self.hidden_node_num)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_gradient_sum[j][k] += hidden_gradient[item][j][k]

                    output_gradient_sum = [[0 for __ in range(self.hidden_node_num + 1)] for _ in range(self.output_node_num)]
                    for item in range(batch_size):
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_gradient_sum[j][k] += output_gradient[item][j][k]

                    for j in range(self.hidden_node_num):
                        for k in range(self.input_node_num + 1):
                            self.hidden_weight[j][k] -= lr * hidden_gradient_sum[j][k] / len(x_batch_list)

                    for j in range(self.output_node_num):
                        for k in range(self.hidden_node_num + 1):
                            self.output_weight[j][k] -= lr * output_gradient_sum[j][k] / len(x_batch_list)
                self.loss_values.append(epoch_loss / len(x_train))
                self.accuracy_list.append(cnt / len(x_train))
                if isinstance(x_valid, list) and isinstance(y_valid, list):

                    valid_epoch_loss = 0
                    valid_cnt = 0
                    for i in range(len(x_valid)):
                        x_sample = [x_valid[i][index] for index in range(len(x_valid[i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = [0 for num in range(self.output_node_num)]
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]

                        predict_list = []
                        for j in range(self.output_node_num):
                            predict = activation_function.softmax(j, output_layer_output)
                            predict_list.append(predict)

                        pred_result = [0 for num in range(self.output_node_num)]
                        max_prob = max(predict_list)
                        index = predict_list.index(max_prob)
                        pred_result[index] = 1

                        if pred_result == y_valid[i]:
                            valid_cnt += 1
                        epsilon = 1e-10
                        categorical_cross_entropy_loss = 0
                        for j in range(self.output_node_num):
                            categorical_cross_entropy_loss += -y_valid[i][j] * np.log(predict_list[j])
                        valid_epoch_loss += categorical_cross_entropy_loss  # 累加损失
                    self.valid_loss_values.append(valid_epoch_loss / len(x_valid))
                    self.valid_accuracy_list.append(valid_cnt / len(x_valid))
                if (_ + 1) % verbose_frequency == 0:
                    text += f'损失：{self.loss_values[-1]}，准确率：{self.accuracy_list[-1] * 100}%'
                    if isinstance(x_valid, list) and isinstance(y_valid, list):
                        text += f"，验证集损失：{self.valid_loss_values[-1]}，验证集准确率：{self.valid_accuracy_list[-1] * 100}%"
                    print(text)

                if isinstance(x_valid, list) and isinstance(y_valid, list) and self.validation_set_early_stop is not False:
                    if self.valid_loss_values[-1] < self.min_valid_loss:
                        self.min_valid_cnt = 0
                        self.min_valid_loss = self.valid_loss_values[-1]
                        if self.early_stop_memory is True:
                            self.hidden_weight_early_stop_memory = copy.deepcopy(self.hidden_weight)
                            self.output_weight_early_stop_memory = copy.deepcopy(self.output_weight)
                    else:
                        self.min_valid_cnt += 1

                if self.min_valid_cnt == self.validation_set_early_stop and self.validation_set_early_stop is not False:
                    if self.early_stop_memory is True:
                        self.hidden_weight = copy.deepcopy(self.hidden_weight_early_stop_memory)
                        self.output_weight = copy.deepcopy(self.output_weight_early_stop_memory)
                    print(f'验证集损失{self.validation_set_early_stop}代不减小，提前终止')
                    break

            if isinstance(x_valid, list) and isinstance(y_valid, list):
                return self.loss_values, self.accuracy_list, self.valid_loss_values, self.valid_accuracy_list
            else:
                return self.loss_values, self.accuracy_list

        if self.target == 'output_1_node_regress':
            for _ in tqdm(range(epochs)):
                text = f'第{_ + 1}代'
                if isinstance(methods, dict):
                    if 'lr_decay' in methods:
                        lr = lr0 * np.exp(-methods['lr_decay'][1] * _)
                        text += f'学习率：{lr}，'

                indices = list(range(len(x_train)))
                random.shuffle(indices)

                # 使用打乱的索引重新排序两个列表
                x_random_train = [x_train[index] for index in indices]
                y_random_train = [y_train[index] for index in indices]

                x_batch_list = []
                y_batch_list = []
                for i in range(len(x_random_train) // batch_size):
                    x_batch_list.append(x_random_train[batch_size * i:batch_size * (i + 1)])
                    y_batch_list.append(y_random_train[batch_size * i:batch_size * (i + 1)])

                epoch_loss = 0

                for batch in range(len(x_random_train) // batch_size):

                    hidden_gradient = []
                    output_gradient = []

                    for i in range(len(x_batch_list[batch])):

                        x_sample = [x_batch_list[batch][i][index] for index in range(len(x_batch_list[batch][i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = 0
                        for j in range(self.hidden_node_num + 1):
                            output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]



                        epsilon = 1e-10
                        mse = 0.5 * (output_layer_output - y_batch_list[batch][i]) ** 2

                        epoch_loss += mse  # 累加损失

                        sample_gradient = []
                        for j in range(self.hidden_node_num):
                            gradient = []
                            for k in range(self.input_node_num + 1):
                                gradient.append((output_layer_output - y_batch_list[batch][i]) * self.output_weight[j] * ac_derivative(
                                    hidden_layer_output[j]) * x_sample[k])
                            sample_gradient.append(gradient)
                        hidden_gradient.append(sample_gradient)
                        sample_gradient = []
                        for j in range(self.hidden_node_num + 1):
                            sample_gradient.append((output_layer_output - y_batch_list[batch][i]) * hidden_layer_ac_output[j])
                        output_gradient.append(sample_gradient)

                    hidden_gradient_sum = [[0 for num in range(self.input_node_num + 1)] for _ in range(self.hidden_node_num)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_gradient_sum[j][k] += hidden_gradient[item][j][k]

                    output_gradient_sum = [0 for num in range(self.hidden_node_num + 1)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num + 1):
                            output_gradient_sum[j] += output_gradient[item][j]

                    for j in range(self.hidden_node_num):
                        for k in range(self.input_node_num + 1):
                            self.hidden_weight[j][k] -= lr * hidden_gradient_sum[j][k] / len(x_batch_list)

                    for j in range(self.hidden_node_num + 1):
                        self.output_weight[j] -= lr * output_gradient_sum[j] / len(x_batch_list)
                self.loss_values.append(epoch_loss / len(x_train))

                if isinstance(x_valid, list) and isinstance(y_valid, list):
                    valid_epoch_loss = 0
                    for i in range(len(x_valid)):
                        x_sample = [x_valid[i][index] for index in range(len(x_valid[i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = 0
                        for j in range(self.hidden_node_num + 1):
                            output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

                        mse = 0.5 * (output_layer_output - y_valid[i]) ** 2

                        valid_epoch_loss += mse

                    self.valid_loss_values.append(valid_epoch_loss / len(x_valid))

                if (_ + 1) % verbose_frequency == 0:
                    text += f'损失：{self.loss_values[-1]}'
                    if isinstance(x_valid, list) and isinstance(y_valid, list):
                        text += f"，验证集损失：{self.valid_loss_values[-1]}"
                    print(text)

                if isinstance(x_valid, list) and isinstance(y_valid, list) and self.validation_set_early_stop is not False:
                    if self.valid_loss_values[-1] < self.min_valid_loss:
                        self.min_valid_cnt = 0
                        self.min_valid_loss = self.valid_loss_values[-1]
                        if self.early_stop_memory is True:
                            self.hidden_weight_early_stop_memory = copy.deepcopy(self.hidden_weight)
                            self.output_weight_early_stop_memory = copy.deepcopy(self.output_weight)
                    else:
                        self.min_valid_cnt += 1

                if self.min_valid_cnt == self.validation_set_early_stop and self.validation_set_early_stop is not False:
                    if self.early_stop_memory is True:
                        self.hidden_weight = copy.deepcopy(self.hidden_weight_early_stop_memory)
                        self.output_weight = copy.deepcopy(self.output_weight_early_stop_memory)
                    print(f'验证集损失{self.validation_set_early_stop}代不减小，提前终止')
                    break


            if isinstance(x_valid, list) and isinstance(y_valid, list):
                return self.loss_values, self.valid_loss_values
            else:
                return self.loss_values

        if self.target == 'output_multi_node_regress':
            for _ in tqdm(range(epochs)):
                text = f'第{_ + 1}代'
                if isinstance(methods, dict):
                    if 'lr_decay' in methods:
                        lr = lr0 * np.exp(-methods['lr_decay'][1] * _)
                        text += f'学习率：{lr}，'

                indices = list(range(len(x_train)))
                random.shuffle(indices)

                # 使用打乱的索引重新排序两个列表
                x_random_train = [x_train[index] for index in indices]
                y_random_train = [y_train[index] for index in indices]

                x_batch_list = []
                y_batch_list = []
                for i in range(len(x_random_train) // batch_size):
                    x_batch_list.append(x_random_train[batch_size * i:batch_size * (i + 1)])
                    y_batch_list.append(y_random_train[batch_size * i:batch_size * (i + 1)])

                epoch_loss = 0

                for batch in range(len(x_random_train) // batch_size):

                    hidden_gradient = []
                    output_gradient = []

                    for i in range(len(x_batch_list[batch])):

                        x_sample = [x_batch_list[batch][i][index] for index in range(len(x_batch_list[batch][i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = [0 for num in range(self.output_node_num)]
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]


                        epsilon = 1e-10
                        mse = 0
                        for j in range(self.output_node_num):
                            mse += 0.5 * (output_layer_output[j] - y_batch_list[batch][i][j]) ** 2

                        epoch_loss += mse  # 累加损失

                        sample_gradient = []
                        for j in range(self.hidden_node_num):
                            gradient = []
                            for k in range(self.input_node_num + 1):
                                sigma = 0
                                for p in range(self.output_node_num):
                                    sigma += self.output_weight[p][j] * (output_layer_output[p] - y_batch_list[batch][i][p])

                                gradient.append(sigma * ac_derivative(hidden_layer_output[j]) * x_sample[k])
                            sample_gradient.append(gradient)
                        hidden_gradient.append(sample_gradient)
                        sample_gradient = []
                        for j in range(self.output_node_num):
                            gradient = []
                            for k in range(self.hidden_node_num + 1):
                                gradient.append(
                                    (output_layer_output[j] - y_batch_list[batch][i][j]) * hidden_layer_ac_output[k])
                            sample_gradient.append(gradient)
                        output_gradient.append(sample_gradient)

                    hidden_gradient_sum = [[0 for __ in range(self.input_node_num + 1)] for _ in
                                           range(self.hidden_node_num)]
                    for item in range(batch_size):
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_gradient_sum[j][k] += hidden_gradient[item][j][k]

                    output_gradient_sum = [[0 for __ in range(self.hidden_node_num + 1)] for _ in
                                           range(self.output_node_num)]
                    for item in range(batch_size):
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_gradient_sum[j][k] += output_gradient[item][j][k]

                    for j in range(self.hidden_node_num):
                        for k in range(self.input_node_num + 1):
                            self.hidden_weight[j][k] -= lr * hidden_gradient_sum[j][k] / len(x_batch_list)

                    for j in range(self.output_node_num):
                        for k in range(self.hidden_node_num + 1):
                            self.output_weight[j][k] -= lr * output_gradient_sum[j][k] / len(x_batch_list)
                self.loss_values.append(epoch_loss / len(x_train))

                if isinstance(x_valid, list) and isinstance(y_valid, list):
                    valid_epoch_loss = 0
                    for i in range(len(x_valid)):
                        x_sample = [x_valid[i][index] for index in range(len(x_valid[i]))]
                        x_sample.append(1)
                        hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            for k in range(self.input_node_num + 1):
                                hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                        hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                        for j in range(self.hidden_node_num):
                            hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                        hidden_layer_ac_output.append(1)

                        output_layer_output = [0 for num in range(self.output_node_num)]
                        for j in range(self.output_node_num):
                            for k in range(self.hidden_node_num + 1):
                                output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]

                        mse = 0
                        for j in range(self.output_node_num):
                            mse += 0.5 * (output_layer_output[j] - y_valid[i][j]) ** 2

                        valid_epoch_loss += mse  # 累加损失

                    self.valid_loss_values.append(valid_epoch_loss / len(x_valid))

                if (_ + 1) % verbose_frequency == 0:
                    text += f'损失：{self.loss_values[-1]}'
                    if isinstance(x_valid, list) and isinstance(y_valid, list):
                        text += f"，验证集损失：{self.valid_loss_values[-1]}"
                    print(text)

                if isinstance(x_valid, list) and isinstance(y_valid, list) and self.validation_set_early_stop is not False:
                    if self.valid_loss_values[-1] < self.min_valid_loss:
                        self.min_valid_cnt = 0
                        self.min_valid_loss = self.valid_loss_values[-1]
                        if self.early_stop_memory is True:
                            self.hidden_weight_early_stop_memory = copy.deepcopy(self.hidden_weight)
                            self.output_weight_early_stop_memory = copy.deepcopy(self.output_weight)
                    else:
                        self.min_valid_cnt += 1

                if self.min_valid_cnt == self.validation_set_early_stop and self.validation_set_early_stop is not False:
                    if self.early_stop_memory is True:
                        self.hidden_weight = copy.deepcopy(self.hidden_weight_early_stop_memory)
                        self.output_weight = copy.deepcopy(self.output_weight_early_stop_memory)
                    print(f'验证集损失{self.validation_set_early_stop}代不减小，提前终止')
                    break

            if isinstance(x_valid, list) and isinstance(y_valid, list):
                return self.loss_values, self.valid_loss_values
            else:
                return self.loss_values

    def predict(self, x):
        if self.target == '2_classify':
            ac = getattr(activation_function, self.hidden_activation)
            x_sample = [x[index] for index in range(len(x))]
            x_sample.append(1)
            hidden_layer_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                for k in range(self.input_node_num + 1):
                    hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

            hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

            hidden_layer_ac_output.append(1)

            output_layer_output = 0
            for j in range(self.hidden_node_num + 1):
                output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

            predict = activation_function.sigmoid(output_layer_output)

            pred_result = 1 if predict >= 0.5 else 0


            return pred_result
        if self.target == 'output_1_node_regress':
            ac = getattr(activation_function, self.hidden_activation)
            x_sample = [x[index] for index in range(len(x))]
            x_sample.append(1)
            hidden_layer_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                for k in range(self.input_node_num + 1):
                    hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

            hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

            hidden_layer_ac_output.append(1)

            output_layer_output = 0
            for j in range(self.hidden_node_num + 1):
                output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]



            return output_layer_output

        if self.target == 'multi_classify':
            ac = getattr(activation_function, self.hidden_activation)
            x_sample = [x[index] for index in range(len(x))]
            x_sample.append(1)
            hidden_layer_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                for k in range(self.input_node_num + 1):
                    hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

            hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

            hidden_layer_ac_output.append(1)

            output_layer_output = [0 for num in range(self.output_node_num)]
            for j in range(self.output_node_num):
                for k in range(self.hidden_node_num + 1):
                    output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]

            predict_list = []
            for j in range(self.output_node_num):
                predict = activation_function.softmax(j, output_layer_output)
                predict_list.append(predict)

            pred_result = [0 for num in range(self.output_node_num)]
            max_prob = max(predict_list)
            index = predict_list.index(max_prob)
            pred_result[index] = 1
            return pred_result

        if self.target == 'output_multi_node_regress':
            ac = getattr(activation_function, self.hidden_activation)
            x_sample = [x[index] for index in range(len(x))]
            x_sample.append(1)
            hidden_layer_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                for k in range(self.input_node_num + 1):
                    hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

            hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
            for j in range(self.hidden_node_num):
                hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

            hidden_layer_ac_output.append(1)

            output_layer_output = [0 for num in range(self.output_node_num)]
            for j in range(self.output_node_num):
                for k in range(self.hidden_node_num + 1):
                    output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]
            return output_layer_output


    def multi_predict(self, x_list):
        if self.target == '2_classify':
            ac = getattr(activation_function, self.hidden_activation)
            pred_list = []
            for i in range(len(x_list)):
                x_sample = [x_list[i][index] for index in range(len(x_list[i]))]
                x_sample.append(1)
                hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    for k in range(self.input_node_num + 1):
                        hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                hidden_layer_ac_output.append(1)

                output_layer_output = 0
                for j in range(self.hidden_node_num + 1):
                    output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

                predict = activation_function.sigmoid(output_layer_output)

                pred_result = 1 if predict >= 0.5 else 0
                pred_list.append(pred_result)
            return pred_list
        if self.target == 'output_1_node_regress':
            ac = getattr(activation_function, self.hidden_activation)
            pred_list = []
            for i in range(len(x_list)):
                x_sample = [x_list[i][index] for index in range(len(x_list[i]))]
                x_sample.append(1)
                hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    for k in range(self.input_node_num + 1):
                        hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                hidden_layer_ac_output.append(1)

                output_layer_output = 0
                for j in range(self.hidden_node_num + 1):
                    output_layer_output += self.output_weight[j] * hidden_layer_ac_output[j]

                pred_list.append(output_layer_output)
            return pred_list
        if self.target == 'multi_classify':
            ac = getattr(activation_function, self.hidden_activation)
            pred_list = []
            for i in range(len(x_list)):
                x_sample = [x_list[i][index] for index in range(len(x_list[i]))]
                x_sample.append(1)
                hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    for k in range(self.input_node_num + 1):
                        hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                hidden_layer_ac_output.append(1)

                output_layer_output = [0 for num in range(self.output_node_num)]
                for j in range(self.output_node_num):
                    for k in range(self.hidden_node_num + 1):
                        output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]

                predict_list = []
                for j in range(self.output_node_num):
                    predict = activation_function.softmax(j, output_layer_output)
                    predict_list.append(predict)

                pred_result = [0 for num in range(self.output_node_num)]
                max_prob = max(predict_list)
                index = predict_list.index(max_prob)
                pred_result[index] = 1
                pred_list.append(pred_result)
            return pred_list

        if self.target == 'output_multi_node_regress':
            ac = getattr(activation_function, self.hidden_activation)
            pred_list = []
            for i in range(len(x_list)):
                x_sample = [x_list[i][index] for index in range(len(x_list[i]))]
                x_sample.append(1)
                hidden_layer_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    for k in range(self.input_node_num + 1):
                        hidden_layer_output[j] += self.hidden_weight[j][k] * x_sample[k]

                hidden_layer_ac_output = [0 for num in range(self.hidden_node_num)]
                for j in range(self.hidden_node_num):
                    hidden_layer_ac_output[j] = ac(hidden_layer_output[j])

                hidden_layer_ac_output.append(1)

                output_layer_output = [0 for num in range(self.output_node_num)]
                for j in range(self.output_node_num):
                    for k in range(self.hidden_node_num + 1):
                        output_layer_output[j] += self.output_weight[j][k] * hidden_layer_ac_output[k]
                pred_list.append(output_layer_output)
            return pred_list

class SOM:
    def __init__(self, input_node_num, height=5, width=5, random_weight_range=5):
        self.input_node_num = input_node_num
        self.height = height
        self.width = width
        SOM_weight = []
        for i in range(height):
            weight = []
            for j in range(width):
                dimension_weight = []
                for k in range(input_node_num):
                    dimension_weight.append(random.random() * random_weight_range * 2 - random_weight_range)
                weight.append(dimension_weight)

            SOM_weight.append(weight)

        self.SOM_weight = SOM_weight
        self.dist_values = []

    def train(self, x, lr=0.01, epochs=100, start_range=4, verbose_frequency=1):

        for _ in tqdm(range(epochs)):
            field_range = basic_function.decay(_, epochs, start_range)
            min_dist_list = []
            for i in range(len(x)):

                min_dist = math.inf
                for j in range(self.height):
                    dist = []
                    for k in range(self.width):
                        dist_cal = basic_function.o_dist(x[i], self.SOM_weight[j][k])
                        dist.append(dist_cal)
                        if dist_cal < min_dist:
                            min_dist = dist_cal
                            min_dist_pos = [j, k]

                min_dist_list.append(min_dist)
                for j in range(self.height):
                    for k in range(self.width):
                        node_dist = basic_function.o_dist(min_dist_pos, [j, k])

                        for dim in range(self.input_node_num):
                            self.SOM_weight[j][k][dim] += lr * basic_function.hci(node_dist, field_range) * (
                                        x[i][dim] - self.SOM_weight[j][k][dim])
            if (_ + 1) % verbose_frequency == 0:
                print(f"第{_ + 1}代平均最小距离：{sum(min_dist_list) / len(x)}")
            self.dist_values.append(sum(min_dist_list) / len(x))
        return self.dist_values

    def predict(self, x):

        clu_result = []

        for i in range(self.height):
            row_list = []
            for j in range(self.width):
                row_list.append([])
            clu_result.append(row_list)

        for i in range(len(x)):

            min_dist = math.inf
            for j in range(5):
                dist = []
                for k in range(5):
                    dist_cal = basic_function.o_dist(x[i], self.SOM_weight[j][k])
                    dist.append(dist_cal)
                    if dist_cal < min_dist:
                        min_dist = dist_cal
                        min_dist_pos = [j, k]
            clu_result[min_dist_pos[0]][min_dist_pos[1]].append(x[i])
        return clu_result



