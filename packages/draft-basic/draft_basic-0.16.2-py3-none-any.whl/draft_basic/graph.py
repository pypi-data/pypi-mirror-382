import matplotlib.pyplot as plt
import warnings

def draw_linechart(data, label, x_interval=1, graph_name='graph', x_label='epoch',y_label='y_label', color=None, figsize=(10, 5), show_plot=True, data_epoch_average=False, plot_save=False):
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑字体
    plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示问题
    if len(data) == 0:
        assert ValueError(f"数据为空")
    if len(data) > 8 and color is None:
        assert ValueError(f"默认只支持最多8种数据，请减少数据种类，若需展示更多数据请利用颜色自定义功能定义颜色")
    if color is None:
        color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'purple']
    first_data = data[0]
    for i in range(len(data)):
        if len(first_data) != len(data[i]):
            warnings.warn("data中每种数据数量不一致", RuntimeWarning)
    if len(data) != len(label):
        assert ValueError(f"数据种数需与标签数量相同")


    plt.figure(figsize=figsize)

    if data_epoch_average is False or data_epoch_average == 1:
        epochs_list = []

        for i in range(len(data)):
            epochs_list.append([j for j in range(1, len(data[i]) + 1)])


        for i in range(len(data)):
            plt.plot(epochs_list[i], data[i], label=label[i], color=color[i])

    else:

        epochs_list = []
        data_list = []
        for i in range(len(data)):
            epochs_list.append([j for j in range(data_epoch_average // 2, (len(data[i])) // data_epoch_average * data_epoch_average, data_epoch_average)])
            single_data_list = []
            if len(data[i]) < 2 * data_epoch_average:
                warnings.warn(f"第{i}个数据需保证其长度（代数）至少为data_epoch_average的两倍，才可展示出曲线", RuntimeWarning)
            elif len(data[i]) % data_epoch_average != 0:
                warnings.warn(f"第{i}个数据长度（代数）不是data_epoch_average的倍数，最后{len(data[i]) % data_epoch_average}代的平均损失不展示", RuntimeWarning)
            for j in range(len(data[i]) // data_epoch_average):


                sum_data = 0

                for k in range(data_epoch_average):
                    sum_data += data[i][j * data_epoch_average + k]

                single_data_list.append(sum_data / data_epoch_average)

            data_list.append(single_data_list)


        for i in range(len(data)):
            plt.plot(epochs_list[i], data_list[i], label=label[i], color=color[i])


    max_length = 0
    for i in range(len(data)):
        if len(data[i]) > max_length:
            max_length = len(data[i])

    # 设置 x 轴刻度为整数
    plt.xticks(range(0, max_length + 1, x_interval))
    plt.title(graph_name)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid()
    if plot_save is not False:
        if plot_save is True:
            plt.savefig('figure')
        else:
            plt.savefig(plot_save)
    if show_plot is True:
        plt.show()


def draw_confusionmatrix(con_matrix, index, show_plot=True):
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑字体
    plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示问题
    fig, ax = plt.subplots()

    ax.axis('off')


    table = ax.table(cellText=con_matrix,  # 表格中的数据
                     loc='center',  # 表格位置
                     cellLoc='center',  # 单元格内文字居中
                     colLabels=index,  # 列标题
                     rowLabels=index)  # 行标题
    table.add_cell(0, -1, width=0.1, height=0.045, text='True/Predict', loc='center')
    # 设置表格样式（可选）
    table.auto_set_font_size(False)
    table.set_fontsize(12)  # 设置字体大小
    table.scale(1.5, 1.5)  # 调整表格的宽度和高度比例


    # 调整布局
    plt.tight_layout()

    if show_plot is True:
        plt.show()
