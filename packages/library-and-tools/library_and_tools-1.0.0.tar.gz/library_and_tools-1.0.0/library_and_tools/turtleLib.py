import turtle


__all__ = [
    "draw_square",
    "draw_rectangle",
    "draw_triangle",
    "draw_circle",
    "draw_star",
    "draw_pentagon",
    "draw_hexagon",
    "draw_smiley",
    "draw_sad",
    "draw_angry",
    "draw_surprised",
    "draw_cat",
    "draw_dog",
    "draw_fish",
    "draw_bird",
    "draw_rabbit",
    "draw_turtle",
    "draw_heart",
    "draw_flower",
    "draw_sun"
]

# إعداد السلحفاة
t = turtle.Turtle()
t.speed(5)


# 🧱 دوال تحكم أساسية
def forward(distance):
    t.forward(distance)


def backward(distance):
    t.backward(distance)


def left(angle):
    t.left(angle)


def right(angle):
    t.right(angle)


def penup():
    t.penup()


def pendown():
    t.pendown()


def goto(x, y):
    t.goto(x, y)


def setheading(angle):
    t.setheading(angle)


def home():
    t.home()


def clear():
    t.clear()


def reset():
    t.reset()


def color(c):
    t.color(c)


def bgcolor(c):
    turtle.bgcolor(c)


def pensize(size):
    t.pensize(size)


def speed(s):
    t.speed(s)


def circle(radius):
    t.circle(radius)


def write(text, font=("Arial", 20, "normal")):
    t.write(text, font=font)


def hide():
    t.hideturtle()


def show():
    t.showturtle()


def done():
    turtle.done()


# ⚙️ إعدادات المستخدم للرسم
def user_settings():
    print("\n🎨 إعدادات الرسم:")

    c = input("🖍️ اختر لون (مثلاً: red, blue, green): ").strip() or "black"

    s = input("⚡ اختر السرعة (من 1 لـ 10): ").strip()

    p = input("📏 اختر حجم القلم (رقم): ").strip()

    try:
        speed(int(s)) if s else None
        pensize(int(p)) if p else None
    except:
        print("⚠️ تم استخدام الإعدادات الافتراضية")

    color(c)


# 🎨 نوع الرسم
def draw_shape():
    print("\n🎨 اختار نوع الرسمة:")
    print("1️⃣ شكل هندسي")
    print("2️⃣ حيوان")
    print("3️⃣ إيموجي وجه")

    choice = input("اكتب الرقم: ").strip()

    if choice == "1":
        draw_geometric()

    elif choice == "2":
        draw_animal()

    elif choice == "3":
        draw_emoji()

    else:
        print("❌ اختيار غير صحيح")


# 🔺 الأشكال الهندسية
def draw_geometric():
    print("\n🟢 الأشكال المتاحة: مربع، مستطيل، مثلث، دائرة، نجمة، سداسي، قلب، بيت")

    shape = input("اكتب اسم الشكل: ").strip()

    user_settings()

    if shape == "مربع":
        for _ in range(4):
            forward(100)
            right(90)

    elif shape == "مستطيل":
        for _ in range(2):
            forward(150)
            right(90)
            forward(80)
            right(90)

    elif shape == "مثلث":
        for _ in range(3):
            forward(100)
            right(120)

    elif shape == "دائرة":
        circle(60)

    elif shape == "نجمة":
        for _ in range(5):
            forward(100)
            right(144)

    elif shape == "سداسي":
        for _ in range(6):
            forward(80)
            right(60)

    elif shape == "قلب":
        t.begin_fill()
        t.left(140)
        t.forward(113)

        for _ in range(200):
            t.right(1)
            t.forward(1)

        t.left(120)

        for _ in range(200):
            t.right(1)
            t.forward(1)

        t.forward(112)
        t.end_fill()

    elif shape == "بيت":
        for _ in range(4):
            forward(100)
            right(90)

        goto(0, 0)
        setheading(45)

        for _ in range(2):
            forward(70)
            right(90)

    else:
        print("❌ الشكل غير موجود")


# 🐾 الحيوانات
def draw_animal():
    print("\n🐾 الحيوانات المتاحة: كلب، قطة، أسد، سمكة، حصان، سلحفاة، طائر، فراشة، أرنب")

    animal = input("اكتب اسم الحيوان: ").strip()

    user_settings()

    animals = {
        "كلب": "🐶",
        "قطة": "🐱",
        "أسد": "🦁",
        "سمكة": "🐟",
        "حصان": "🐴",
        "سلحفاة": "🐢",
        "طائر": "🐦",
        "فراشة": "🦋",
        "أرنب": "🐰"
    }

    if animal in animals:
        write(animals[animal], ("Arial", 60, "normal"))

    else:
        print("❌ الحيوان غير متاح")


# 😀 إيموجيات الوجوه فقط
def draw_emoji():
    print("\n😀 الإيموجيات المتاحة:")
    print("سعيد، ضاحك، حزين، غاضب، متفاجئ، نائم، مغمض، بيغمز، باكي، مرتبك، محرج، مريض، مبسوط قوي، بيحب، خايف")

    emoji = input("اكتب اسم الإيموجي: ").strip()

    user_settings()

    emojis = {
        "سعيد": "😊",
        "ضاحك": "😂",
        "حزين": "😢",
        "غاضب": "😡",
        "متفاجئ": "😮",
        "نائم": "😴",
        "مغمض": "😌",
        "بيغمز": "😉",
        "باكي": "😭",
        "مرتبك": "😕",
        "محرج": "😳",
        "مريض": "🤒",
        "مبسوط قوي": "😁",
        "بيحب": "😍",
        "خايف": "😱"
    }

    if emoji in emojis:
        write(emojis[emoji], ("Arial", 60, "normal"))

    else:
        print("❌ الإيموجي مش موجود")


# ✨ تشغيل مباشر لو الملف اتنفذ لوحده
if __name__ == "__main__":
    draw_shape()
    done()
    

