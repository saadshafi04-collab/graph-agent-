import matplotlib.pyplot as plt
import io
import base64


def chart_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return image_base64


def line_chart(data, title, y_label):
    fig, ax = plt.subplots()
    dates = [row["date"] for row in data]
    values = [row["value"] for row in data]
    ax.plot(dates, values)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Date")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return chart_to_base64(fig)


def bar_chart(data, title):
    fig, ax = plt.subplots()
    labels = [row["type"] for row in data]
    avgs = [row["avg"] for row in data]
    ax.bar(labels, avgs)
    ax.set_title(title)
    ax.set_ylabel("Average Value")
    fig.tight_layout()
    return chart_to_base64(fig)


def pie_chart(data, title):
    fig, ax = plt.subplots()
    labels = [f"{row['asset']} - {row['status']}" for row in data]
    counts = [row["count"] for row in data]
    ax.pie(counts, labels=labels, autopct="%1.1f%%")
    ax.set_title(title)
    fig.tight_layout()
    return chart_to_base64(fig)
