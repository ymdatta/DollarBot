import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center')


def visualize(total_text, budgetData):
    colors=['red','cornflowerblue','greenyellow','orange','violet','grey']
    # plot the expense bar chart
    total_text_split = [line for line in total_text.split('\n') if line.strip() != '']
    categ_val = {}
    for i in total_text_split:
        a = i.split(' ')
        a[1] = a[1].replace("$", "")
        categ_val[a[0]] = float(a[1])

    x = list(categ_val.keys())
    y = list(categ_val.values())

    plt.bar(categ_val.keys(), categ_val.values(), color=colors, edgecolor='black')
    addlabels(x, y)

    plt.ylabel("Expenditure")
    plt.xlabel("Categories")
    plt.xticks(rotation=45)

    # plot budget horizontal line
    lines = []
    labels = []
    if isinstance(budgetData, str):
        lines.append(plt.axhline(y=float(budgetData), color="r", linestyle="-"))
        labels.append("overall budget")
    elif isinstance(budgetData, dict):
        colorCnt = 0
        # to avoid the budget override by each others, record the budget and adjust the line
        duplicate = {}
        for key in budgetData.keys():
            val = budgetData[key]
            plotVal = float(val)
            if val in duplicate:
                # if duplicate, move line
                plotVal += 2*duplicate[val]
            lines.append(plt.axhline(y=plotVal, color=colors[colorCnt], linestyle="-"))
            duplicate[val] = duplicate[val] + 1 if val in duplicate else 1
            labels.append(key)
            colorCnt += 1

    plt.legend(lines, labels)
    plt.savefig('expenditure.png', bbox_inches='tight')

    plt.clf()
    plt.cla()
    plt.close()
